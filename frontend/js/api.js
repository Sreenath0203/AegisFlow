/**
 * AegisFlow Centralized API Client Module
 *
 * Handles all communication between the frontend
 * and the AegisFlow FastAPI backend.
 */

const API_BASE = (function () {

  // Explicit frontend override
  if (
    typeof window !== 'undefined' &&
    window.API_BASE_URL
  ) {
    return window.API_BASE_URL.replace(/\/+$/, '');
  }

  // Local development
  if (typeof window !== 'undefined') {

    const origin = window.location.origin;

    if (
      origin.includes(':5500') ||
      origin.includes(':5501') ||
      window.location.protocol === 'file:'
    ) {
      return 'http://127.0.0.1:8000/api/v1';
    }
  }

  // Production / same-origin
  return '/api/v1';

})();


/* ============================================================
   API ERROR
   ============================================================ */

class APIError extends Error {

  constructor(message, status = 0, data = null) {

    super(message);

    this.name = 'APIError';
    this.status = status;
    this.data = data;
  }
}


/* ============================================================
   GENERIC REQUEST FUNCTION
   ============================================================ */

async function request(endpoint, options = {}) {

  const url = `${API_BASE}${endpoint}`;

  const defaultHeaders = {
    'Accept': 'application/json',
    'Content-Type': 'application/json'
  };

  try {

    const response = await fetch(url, {
      ...options,
      headers: {
        ...defaultHeaders,
        ...(options.headers || {})
      }
    });

    let data = null;

    const contentType =
      response.headers.get('content-type') || '';

    if (contentType.includes('application/json')) {

      try {
        data = await response.json();
      } catch (e) {
        data = null;
      }

    } else {

      try {
        data = await response.text();
      } catch (e) {
        data = null;
      }
    }

    if (!response.ok) {

      let message =
        `API Request failed with status ${response.status}`;

      if (data) {

        if (typeof data === 'string') {
          message = data;
        } else if (data.detail) {
          message = data.detail;
        } else if (data.message) {
          message = data.message;
        }
      }

      throw new APIError(
        message,
        response.status,
        data
      );
    }

    return data;

  } catch (error) {

    if (error instanceof APIError) {
      throw error;
    }

    throw new APIError(
      `Network / Connection Error connecting to AegisFlow API at ${url}: ${error.message}`,
      0,
      null
    );
  }
}


/* ============================================================
   API OBJECT
   ============================================================ */

const API = {

  /* ----------------------------------------------------------
     BASE URL
     ---------------------------------------------------------- */

  getApiBase() {
    return API_BASE;
  },


  /* ----------------------------------------------------------
     HEALTH
     ---------------------------------------------------------- */

  async checkHealth() {

    const healthUrl =
      API_BASE.replace(/\/api\/v1\/?$/, '') +
      '/health';

    try {

      const response = await fetch(
        healthUrl,
        {
          method: 'GET',
          headers: {
            'Accept': 'application/json'
          }
        }
      );

      if (response.ok) {
        return await response.json();
      }

      return {
        status: 'unhealthy'
      };

    } catch (error) {

      return {
        status: 'disconnected',
        error: error.message
      };
    }
  },


  /* ----------------------------------------------------------
     DASHBOARD
     ---------------------------------------------------------- */

  async getDashboardSummary() {
    return await request('/dashboard/summary');
  },


  /* ----------------------------------------------------------
     RISKS
     ---------------------------------------------------------- */

  async getRisks() {
    return await request('/risks/');
  },

  async getRiskById(entityId) {
    return await request(`/risks/${entityId}`);
  },


  /* ----------------------------------------------------------
     SUPPLIERS
     ---------------------------------------------------------- */

  async getSuppliers() {
    return await request('/suppliers/');
  },

  async getSupplierById(supplierId) {
    return await request(`/suppliers/${supplierId}`);
  },

  async analyzeSupplierRisk(supplierId) {

    return await request(
      `/suppliers/${supplierId}/analyze`,
      {
        method: 'POST'
      }
    );
  },


  /* ----------------------------------------------------------
     SHIPMENTS
     ---------------------------------------------------------- */

  async getShipments() {
    return await request('/shipments/');
  },

  async getShipmentById(shipmentId) {
    return await request(`/shipments/${shipmentId}`);
  },

  async getShipmentsBySupplier(supplierId) {

    return await request(
      `/shipments?supplier_id=${encodeURIComponent(supplierId)}`
    );
  },


  /* ----------------------------------------------------------
     INVENTORY
     ---------------------------------------------------------- */

  async getInventory() {
    return await request('/inventory/');
  },

  async getInventoryById(itemId) {
    return await request(`/inventory/${itemId}`);
  },


  /* ----------------------------------------------------------
     RECOMMENDATIONS
     ---------------------------------------------------------- */

  async getRecommendations() {
    return await request('/recommendations/');
  },

  async approveRecommendation(recId) {

    return await request(
      `/recommendations/${recId}/approve`,
      {
        method: 'POST'
      }
    );
  },


  /* ----------------------------------------------------------
     SCENARIOS
     ---------------------------------------------------------- */

  async getScenarios(disruptionType = null) {
    const qs = disruptionType ? `?disruption_type=${encodeURIComponent(disruptionType)}` : '';
    return await request(`/scenarios/${qs}`);
  },


  /* ----------------------------------------------------------
     COMPLIANCE
     ---------------------------------------------------------- */

  async getCompliance() {
    return await request('/compliance/');
  },


  /* ----------------------------------------------------------
     NEWS
     ---------------------------------------------------------- */

  async getNews() {
    return await request('/news/');
  },

  async fetchAndStoreNews() {

    return await request(
      '/news/fetch',
      {
        method: 'POST'
      }
    );
  },

  async getNewsImpactChain() {
    return await request('/news/impact-chain');
  },


  /* ----------------------------------------------------------
     REPORTS
     ---------------------------------------------------------- */

  async getReport() {
    return await request('/reports/summary');
  },


  /* ----------------------------------------------------------
     DEMO
     ---------------------------------------------------------- */

  async triggerTyphoonDemo() {

    return await request(
      '/demo/trigger-typhoon-scenario',
      {
        method: 'POST'
      }
    );
  },


  /* ----------------------------------------------------------
     WEATHER
     ---------------------------------------------------------- */

  async getLiveWeather(location) {

    return await request(
      `/ai/weather?location=${encodeURIComponent(location)}`
    );
  },


  /* ==========================================================
     EXISTING AEGISFLOW CHAT
     ========================================================== */

  async chatWithAI(message, history = null) {

    return await request(
      '/ai/chat',
      {
        method: 'POST',

        body: JSON.stringify({
          message: message,
          conversation_history: history
        })
      }
    );
  },


  /* ==========================================================
     IBM WATSONX ORCHESTRATE CHAT
     ========================================================== */

  async chatWithOrchestrate(
    message,
    history = null,
    threadId = null
  ) {

    const body = {
      message: message,
      conversation_history: history
    };

    // Pass thread_id when continuing an existing conversation
    if (threadId) {
      body.thread_id = threadId;
    }

    const data = await request(
      '/ai/orchestrate-chat',
      {
        method: 'POST',
        body: JSON.stringify(body)
      }
    );

    /*
     * Backend currently returns:
     *
     * {
     *   status: "success",
     *   response: "...",
     *   thread_id: "...",
     *   run_id: "...",
     *   task_id: null,
     *   message_id: "..."
     * }
     *
     * Some versions may wrap the actual result
     * inside data.response.
     */

    return normalizeOrchestrateResponse(data);
  }

};


/* ============================================================
   NORMALIZE IBM ORCHESTRATE RESPONSE
   ============================================================ */

function normalizeOrchestrateResponse(data) {

  if (!data) {

    return {
      response: '',
      thread_id: null,
      run_id: null,
      task_id: null,
      message_id: null,
      tools_used: []
    };
  }


  /*
   * Case 1:
   *
   * {
   *   status: "success",
   *   response: "actual text",
   *   thread_id: "..."
   * }
   */

  if (typeof data.response === 'string') {

    return {
      response: data.response,

      thread_id:
        data.thread_id ||
        data.threadId ||
        null,

      run_id:
        data.run_id ||
        data.runId ||
        null,

      task_id:
        data.task_id ||
        data.taskId ||
        null,

      message_id:
        data.message_id ||
        data.messageId ||
        null,

      tools_used:
        Array.isArray(data.tools_used)
          ? data.tools_used
          : []
    };
  }


  /*
   * Case 2:
   *
   * {
   *   status: "success",
   *   response: {
   *      response: "...",
   *      thread_id: "..."
   *   }
   * }
   */

  if (
    data.response &&
    typeof data.response === 'object'
  ) {

    const result = data.response;

    return {
      response:
        result.response ||
        result.text ||
        result.content ||
        '',

      thread_id:
        result.thread_id ||
        result.threadId ||
        data.thread_id ||
        null,

      run_id:
        result.run_id ||
        result.runId ||
        data.run_id ||
        null,

      task_id:
        result.task_id ||
        result.taskId ||
        data.task_id ||
        null,

      message_id:
        result.message_id ||
        result.messageId ||
        data.message_id ||
        null,

      tools_used:
        Array.isArray(result.tools_used)
          ? result.tools_used
          : []
    };
  }


  /*
   * Fallback
   */

  return {
    response:
      data.text ||
      data.content ||
      data.message ||
      '',

    thread_id:
      data.thread_id ||
      data.threadId ||
      null,

    run_id:
      data.run_id ||
      data.runId ||
      null,

    task_id:
      data.task_id ||
      data.taskId ||
      null,

    message_id:
      data.message_id ||
      data.messageId ||
      null,

    tools_used:
      Array.isArray(data.tools_used)
        ? data.tools_used
        : []
  };
}


/* ============================================================
   GLOBAL EXPORT
   ============================================================ */

if (typeof window !== 'undefined') {

  window.API = API;

  window.APIError = APIError;

}