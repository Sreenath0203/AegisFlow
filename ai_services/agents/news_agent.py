from ai_services.agents.base_agent import BaseAgent
from typing import Dict, Any, List
import requests
import urllib.parse
import xml.etree.ElementTree as ET
from datetime import datetime, timezone, timedelta
import email.utils


class NewsAgent(BaseAgent):
    """
    Live Global Supply Chain News Agent.

    Primary provider:
        GDELT

    Fallback provider:
        Google News RSS

    IMPORTANT:
        This agent never invents news.

        All articles come from external live news providers.
        The agent only classifies and filters those articles.
    """

    def __init__(self):
        super().__init__(
            name="News Agent",
            role="Live Global Supply Chain News Intelligence"
        )

    # =========================================================
    # BUILD QUERY
    # =========================================================

    def _build_query(
        self,
        locations: List[str],
        suppliers: List[str],
        products: List[str],
        industries: List[str]
    ) -> str:

        targets = []

        for value in (
            locations[:8]
            + suppliers[:5]
            + products[:5]
            + industries[:3]
        ):

            value = str(value).strip()

            if value:
                targets.append(f'"{value}"')

        if targets:
            target_query = "(" + " OR ".join(targets) + ")"
        else:
            target_query = '"supply chain"'

        disruption_terms = (
            'port OR '
            'shipping OR '
            'logistics OR '
            '"supply chain" OR '
            'cargo OR '
            'freight OR '
            'supplier OR '
            'shortage OR '
            'congestion OR '
            'delay OR '
            'disruption OR '
            'shutdown OR '
            'strike OR '
            'typhoon OR '
            'cyclone OR '
            'hurricane OR '
            'earthquake OR '
            'flood OR '
            'wildfire OR '
            'tsunami OR '
            'sanctions OR '
            '"export ban" OR '
            '"import ban" OR '
            '"export restriction" OR '
            '"import restriction" OR '
            '"port closure" OR '
            '"shipping disruption" OR '
            '"production halt" OR '
            '"factory closure" OR '
            '"factory shutdown" OR '
            '"supply disruption" OR '
            '"transportation disruption"'
        )

        return f"{target_query} ({disruption_terms})"

    # =========================================================
    # CLASSIFY ARTICLE
    # =========================================================

    def _classify_article(
        self,
        title: str
    ) -> Dict[str, Any]:

        text = title.lower()

        # -----------------------------------------------------
        # REAL DISRUPTION EVENTS
        # -----------------------------------------------------

        high_risk_keywords = [
            "port closure",
            "port closed",
            "port shutdown",
            "port suspended",

            "shipping disruption",
            "shipping halted",
            "shipping suspended",

            "factory shutdown",
            "factory closure",

            "production halt",
            "production halted",
            "production stopped",

            "supply disruption",
            "supply shortage",
            "component shortage",
            "chip shortage",
            "semiconductor shortage",

            "export ban",
            "import ban",
            "export restriction",
            "import restriction",

            "sanctions",

            "logistics disruption",
            "transport disruption",
            "transportation disruption",

            "strike",

            "typhoon",
            "cyclone",
            "hurricane",
            "earthquake",
            "flood",
            "wildfire",
            "tsunami",
            "landslide"
        ]

        # -----------------------------------------------------
        # SUPPORTING OPERATIONAL TERMS
        # -----------------------------------------------------

        operational_keywords = [
            "port",
            "shipping",
            "logistics",
            "cargo",
            "freight",
            "transport",
            "supply chain",
            "supplier",
            "factory",
            "manufacturing",
            "production",
            "warehouse",
            "shipment",
            "container",
            "congestion",
            "delay",
            "shortage",
            "closure",
            "shutdown"
        ]

        # -----------------------------------------------------
        # FINANCIAL NOISE
        # -----------------------------------------------------

        financial_keywords = [
            "stock price",
            "stock market",
            "stock outlook",
            "shares",
            "share price",
            "market cap",
            "earnings",
            "investor",
            "investors",
            "investment",
            "portfolio",
            "wall street",
            "stock rating",
            "buy rating",
            "sell rating",
            "valuation",
            "price target",
            "dividend",
            "trading",
            "analyst",
            "bullish stock",
            "bearish stock"
        ]

        high_matches = [
            keyword
            for keyword in high_risk_keywords
            if keyword in text
        ]

        operational_matches = [
            keyword
            for keyword in operational_keywords
            if keyword in text
        ]

        financial_matches = [
            keyword
            for keyword in financial_keywords
            if keyword in text
        ]

        # -----------------------------------------------------
        # FINANCIAL ARTICLE
        # -----------------------------------------------------

        if financial_matches and not high_matches:

            return {
                "matched_risk_terms": [],
                "financial_terms": financial_matches,
                "relevance": "LOW",
                "severity": "LOW"
            }

        # -----------------------------------------------------
        # STRONG DISRUPTION
        # -----------------------------------------------------

        if high_matches:

            critical_terms = [
                "typhoon",
                "cyclone",
                "hurricane",
                "earthquake",
                "flood",
                "wildfire",
                "tsunami",
                "landslide",
                "port closure",
                "port closed",
                "port shutdown",
                "factory shutdown",
                "factory closure",
                "production halt",
                "production halted",
                "production stopped",
                "shipping halted",
                "supply shortage",
                "component shortage",
                "chip shortage",
                "semiconductor shortage",
                "export ban",
                "import ban",
                "sanctions"
            ]

            is_critical = any(
                term in text
                for term in critical_terms
            )

            return {
                "matched_risk_terms": high_matches,
                "financial_terms": financial_matches,
                "relevance": "HIGH",
                "severity": (
                    "HIGH"
                    if is_critical
                    else "MEDIUM"
                )
            }

        # -----------------------------------------------------
        # ORDINARY SUPPLY CHAIN ARTICLE
        # -----------------------------------------------------

        if len(operational_matches) >= 2:

            return {
                "matched_risk_terms": operational_matches,
                "financial_terms": financial_matches,
                "relevance": "MEDIUM",
                "severity": "LOW"
            }

        # -----------------------------------------------------
        # EVERYTHING ELSE
        # -----------------------------------------------------

        return {
            "matched_risk_terms": [],
            "financial_terms": financial_matches,
            "relevance": "LOW",
            "severity": "LOW"
        }

    # =========================================================
    # DATE FILTER
    # =========================================================

    def _is_recent(
        self,
        published_at: str,
        hours: int = 48
    ) -> bool:

        if not published_at:
            return True

        try:

            # GDELT format:
            # 20260809T023000Z

            if published_at.endswith("Z") and "T" in published_at:

                published = datetime.strptime(
                    published_at,
                    "%Y%m%dT%H%M%SZ"
                ).replace(
                    tzinfo=timezone.utc
                )

            else:

                # Google RSS format:
                # Fri, 07 Aug 2026 22:38:00 GMT

                parsed = email.utils.parsedate_to_datetime(
                    published_at
                )

                published = parsed.astimezone(
                    timezone.utc
                )

            cutoff = (
                datetime.now(timezone.utc)
                - timedelta(hours=hours)
            )

            return published >= cutoff

        except Exception:

            # If the provider gives an unknown date format,
            # keep the article rather than inventing a date.
            return True

    # =========================================================
    # GDELT
    # =========================================================

    def _search_gdelt(
        self,
        query: str,
        max_records: int
    ) -> Dict[str, Any]:

        url = (
            "https://api.gdeltproject.org/"
            "api/v2/doc/doc"
        )

        params = {
            "query": query,
            "mode": "artlist",
            "format": "json",
            "maxrecords": min(
                int(max_records),
                50
            ),
            "timespan": "48h",
            "sort": "datedesc"
        }

        response = requests.get(
            url,
            params=params,
            timeout=15,
            headers={
                "User-Agent":
                    "AegisFlow/1.0 Supply Chain Intelligence"
            }
        )

        if response.status_code == 429:
            raise RuntimeError(
                "GDELT_RATE_LIMITED"
            )

        response.raise_for_status()

        content_type = response.headers.get(
            "content-type",
            ""
        ).lower()

        if (
            "json" not in content_type
            and not response.text.lstrip().startswith("{")
        ):
            raise RuntimeError(
                "GDELT returned a non-JSON response."
            )

        data = response.json()

        articles = []

        for article in data.get(
            "articles",
            []
        ):

            title = article.get(
                "title",
                ""
            ).strip()

            if not title:
                continue

            published = article.get(
                "seendate",
                ""
            )

            if not self._is_recent(
                published,
                48
            ):
                continue

            classification = (
                self._classify_article(
                    title
                )
            )

            if classification["relevance"] == "LOW":
                continue

            articles.append({
                "title": title,
                "url": article.get(
                    "url",
                    ""
                ),
                "source": article.get(
                    "domain",
                    "GDELT"
                ),
                "published_at": published,
                **classification
            })

        return {
            "source": "GDELT Global News",
            "articles": articles
        }

    # =========================================================
    # GOOGLE NEWS RSS
    # =========================================================

    def _search_google_news(
        self,
        query: str,
        max_records: int
    ) -> Dict[str, Any]:

        # Ask Google News for recent results.
        recent_query = (
            query
            + " when:2d"
        )

        encoded_query = urllib.parse.quote(
            recent_query
        )

        url = (
            "https://news.google.com/rss/search"
            f"?q={encoded_query}"
            "&hl=en-US"
            "&gl=US"
            "&ceid=US:en"
        )

        response = requests.get(
            url,
            timeout=15,
            headers={
                "User-Agent":
                    "Mozilla/5.0 "
                    "AegisFlow Supply Chain Intelligence"
            }
        )

        response.raise_for_status()

        root = ET.fromstring(
            response.content
        )

        articles = []

        for item in root.findall(
            ".//item"
        )[:max_records]:

            title = item.findtext(
                "title",
                ""
            ).strip()

            article_url = item.findtext(
                "link",
                ""
            ).strip()

            published = item.findtext(
                "pubDate",
                ""
            ).strip()

            if not title:
                continue

            # IMPORTANT:
            # Do not allow old articles into the live
            # intelligence dashboard.
            if not self._is_recent(
                published,
                48
            ):
                continue

            classification = (
                self._classify_article(
                    title
                )
            )

            if classification["relevance"] == "LOW":
                continue

            source_node = item.find(
                "source"
            )

            source = (
                source_node.text.strip()
                if (
                    source_node is not None
                    and source_node.text
                )
                else "Google News"
            )

            articles.append({
                "title": title,
                "url": article_url,
                "source": source,
                "published_at": published,
                **classification
            })

        return {
            "source": "Google News RSS",
            "articles": articles
        }

    # =========================================================
    # MAIN SEARCH
    # =========================================================

    def search(
        self,
        locations: List[str] = None,
        suppliers: List[str] = None,
        products: List[str] = None,
        industries: List[str] = None,
        max_records: int = 20
    ) -> Dict[str, Any]:

        locations = locations or []
        suppliers = suppliers or []
        products = products or []
        industries = industries or []

        query = self._build_query(
            locations,
            suppliers,
            products,
            industries
        )

        retrieved_at = datetime.now(
            timezone.utc
        ).isoformat()

        # -----------------------------------------------------
        # GDELT
        # -----------------------------------------------------

        try:

            result = self._search_gdelt(
                query,
                max_records
            )

            return {
                "agent": self.name,
                "source": result["source"],
                "status": "ONLINE",
                "query": query,
                "retrieved_at": retrieved_at,
                "article_count": len(
                    result["articles"]
                ),
                "articles": result["articles"]
            }

        except Exception as gdelt_error:

            # -------------------------------------------------
            # GOOGLE NEWS FALLBACK
            # -------------------------------------------------

            try:

                result = self._search_google_news(
                    query,
                    max_records
                )

                return {
                    "agent": self.name,
                    "source": result["source"],
                    "status": "ONLINE_FALLBACK",
                    "primary_provider": "GDELT",
                    "primary_provider_error": str(
                        gdelt_error
                    ),
                    "query": query,
                    "retrieved_at": retrieved_at,
                    "article_count": len(
                        result["articles"]
                    ),
                    "articles": result["articles"]
                }

            except Exception as google_error:

                return {
                    "agent": self.name,
                    "source": "Live News Providers",
                    "status": "UNAVAILABLE",
                    "query": query,
                    "retrieved_at": retrieved_at,
                    "article_count": 0,
                    "articles": [],
                    "message": (
                        "All live news providers "
                        "unavailable."
                    ),
                    "provider_errors": {
                        "gdelt": str(
                            gdelt_error
                        ),
                        "google_news": str(
                            google_error
                        )
                    }
                }

    # =========================================================
    # AGENT ENTRY POINT
    # =========================================================

    def analyze(
        self,
        context: Dict[str, Any]
    ) -> Dict[str, Any]:

        locations = context.get(
            "locations",
            []
        )

        suppliers = context.get(
            "suppliers",
            []
        )

        products = context.get(
            "products",
            []
        )

        industries = context.get(
            "industries",
            []
        )

        if (
            locations
            or suppliers
            or products
            or industries
        ):

            return self.search(
                locations=locations,
                suppliers=suppliers,
                products=products,
                industries=industries
            )

        return {
            "agent": self.name,
            "source": "Live News Providers",
            "status": "NO_TARGETS",
            "article_count": 0,
            "articles": [],
            "message": (
                "No live search targets supplied."
            )
        }


news_agent = NewsAgent()
