import pytest
from fastapi.testclient import TestClient
from backend.main import app

client = TestClient(app)

def test_suppliers_have_coordinates():
    response = client.get("/api/v1/suppliers/")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) > 0
    
    # Check ABC Electronics Co.
    abc = next((s for s in data if s["name"] == "ABC Electronics Co."), None)
    assert abc is not None
    assert abc["latitude"] is not None
    assert abc["longitude"] is not None
    assert abc["country"] == "Taiwan"

def test_shipments_with_supplier_filter_and_coordinates():
    response = client.get("/api/v1/shipments?supplier_id=1")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) > 0
    
    shp = data[0]
    assert shp["shipment_code"] == "SHP-9021"
    assert shp["origin_lat"] is not None
    assert shp["origin_lng"] is not None
    assert shp["dest_lat"] is not None
    assert shp["dest_lng"] is not None

def test_live_weather_endpoint():
    response = client.get("/api/v1/ai/weather?location=Kaohsiung, Taiwan")
    assert response.status_code == 200
    data = response.json()
    assert "temperature_c" in data
    assert "humidity_percent" in data
    assert "weather_risk_level" in data

def test_news_fetch_and_persistent_storage():
    fetch_res = client.post("/api/v1/news/fetch")
    assert fetch_res.status_code == 200
    f_data = fetch_res.json()
    assert f_data["status"] == "SUCCESS"

    news_res = client.get("/api/v1/news/")
    assert news_res.status_code == 200
    news_list = news_res.json()
    assert isinstance(news_list, list)
    assert len(news_list) > 0
    
    # Verify required fields
    first_news = news_list[0]
    assert "headline" in first_news
    assert "severity" in first_news

def test_news_impact_chain():
    response = client.get("/api/v1/news/impact-chain")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) > 0
    
    item = data[0]
    assert "news" in item
    assert "suppliers" in item
    assert "shipments" in item
    assert "inventory" in item
    assert "risks" in item

def test_ai_chatbot_query_abc_electronics():
    payload = {
        "message": "What is the current risk for ABC Electronics?",
        "conversation_history": []
    }
    response = client.post("/api/v1/ai/chat", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert "response" in data
    assert len(data["response"]) > 20
    assert "IBM Granite" in data["model"] or "ibm/granite" in data["model"]
