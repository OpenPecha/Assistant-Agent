from fastapi import APIRouter
from fastapi.responses import HTMLResponse, JSONResponse
from api.config import get

ui_router = APIRouter(tags=["ui"])

@ui_router.get("/config", response_class=JSONResponse)
async def get_config():
    """Endpoint to provide frontend configuration"""
    return {
        "auth0_domain": get("DOMAIN_NAME"),
        "auth0_client_id": get("CLIENT_ID")
    }

@ui_router.get("/", response_class=HTMLResponse)
async def serve_ui():
    return HTML_CONTENT

HTML_CONTENT = """
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8"/>
<meta name="viewport" content="width=device-width, initial-scale=1.0"/>
<title>Assistant Agent</title>
<style>
*,*::before,*::after{box-sizing:border-box;margin:0;padding:0}
:root{
  --bg-primary:#f7f9fc;
  --bg-secondary:#ffffff;
  --bg-tertiary:#e8f0fe;
  --bg-card:#ffffff;
  --bg-input:#f1f5f9;
  --bg-hover:#e2e8f0;
  --text-primary:#1a202c;
  --text-secondary:#4a5568;
  --text-muted:#718096;
  --accent:#e94560;
  --accent-hover:#d63851;
  --accent-green:#38b2ac;
  --accent-blue:#3182ce;
  --accent-purple:#805ad5;
  --border:#e2e8f0;
  --shadow:0 4px 20px rgba(0,0,0,0.08);
  --radius:12px;
  --radius-sm:8px;
  --radius-xs:6px;
  --transition:all 0.2s ease;
}
html,body{height:100%;font-family:'Segoe UI',system-ui,-apple-system,sans-serif;background:var(--bg-primary);color:var(--text-primary);overflow:hidden}
button{cursor:pointer;border:none;font-family:inherit;font-size:inherit}
input,textarea,select{font-family:inherit;font-size:inherit;border:none;outline:none}

.app{display:flex;height:100vh;width:100vw}

/* Sidebar */
.sidebar{
  width:320px;min-width:320px;
  background:var(--bg-secondary);
  border-right:1px solid var(--border);
  display:flex;flex-direction:column;
  overflow:hidden;
}
.sidebar-header{
  padding:20px;border-bottom:1px solid var(--border);
}
.sidebar-header h1{
  font-size:18px;font-weight:700;
  margin-bottom:16px;
}
.token-section{display:flex;flex-direction:column;gap:8px}
.token-section label{font-size:12px;color:var(--text-secondary);font-weight:500;text-transform:uppercase;letter-spacing:0.5px}
.token-input{
  display:flex;gap:8px;
}
.token-input input{
  flex:1;padding:8px 12px;
  background:var(--bg-input);color:var(--text-primary);
  border:1px solid var(--border);border-radius:var(--radius-xs);
  font-size:13px;
}
.token-input input:focus{border-color:var(--accent-blue)}
.btn-sm{
  padding:6px 14px;border-radius:var(--radius-xs);
  font-size:12px;font-weight:600;
  transition:var(--transition);
}
.btn-primary{background:var(--accent);color:#fff}
.btn-primary:hover{background:var(--accent-hover)}
.btn-outline{background:transparent;color:var(--accent-blue);border:1px solid var(--accent-blue)}
.btn-outline:hover{background:var(--accent-blue);color:#fff}
.btn-danger{background:#e53e3e;color:#fff}
.btn-danger:hover{background:#c53030}
.btn-success{background:var(--accent-green);color:#fff}
.btn-success:hover{background:#2c9e94}
.btn-google{background:#4285f4;color:#fff;border:none}
.btn-google:hover{background:#357ae8}

.new-assistant-btn{
  background:var(--accent-blue);
  color:#fff;border-radius:var(--radius-sm);
  margin:16px 20px;padding:12px;
  font-weight:600;font-size:14px;
  transition:var(--transition);
  display:flex;align-items:center;justify-content:center;gap:8px;
}
.new-assistant-btn:hover{opacity:0.9;transform:translateY(-1px)}

.assistant-list{
  flex:1;overflow-y:auto;padding:8px;
}
.assistant-list::-webkit-scrollbar{width:4px}
.assistant-list::-webkit-scrollbar-thumb{background:var(--border);border-radius:4px}

.assistant-item{
  padding:14px 16px;margin-bottom:4px;
  border-radius:var(--radius-sm);
  cursor:pointer;transition:var(--transition);
  border:1px solid transparent;
}
.assistant-item:hover{background:var(--bg-hover);border-color:var(--border)}
.assistant-item.active{background:var(--bg-tertiary);border-color:var(--accent-blue)}
.assistant-item h3{font-size:14px;font-weight:600;margin-bottom:4px;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
.assistant-item p{font-size:12px;color:var(--text-muted);white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
.assistant-item .badge{
  display:inline-block;padding:2px 8px;border-radius:10px;
  font-size:10px;font-weight:600;margin-top:6px;
  background:rgba(66,153,225,0.15);color:var(--accent-blue);
}

.sidebar-footer{
  padding:12px 20px;border-top:1px solid var(--border);
  font-size:11px;color:var(--text-muted);text-align:center;
}

/* Main Area */
.main{flex:1;display:flex;flex-direction:column;overflow:hidden}

/* Empty State */
.empty-state{
  flex:1;display:flex;flex-direction:column;align-items:center;justify-content:center;
  gap:16px;color:var(--text-muted);
}
.empty-state svg{width:80px;height:80px;opacity:0.3}
.empty-state h2{font-size:22px;font-weight:600;color:var(--text-secondary)}
.empty-state p{font-size:14px;max-width:400px;text-align:center;line-height:1.6}

/* Assistant Detail Header */
.detail-header{
  padding:16px 24px;border-bottom:1px solid var(--border);
  display:flex;align-items:center;justify-content:space-between;
  background:var(--bg-secondary);
}
.detail-header-left{display:flex;align-items:center;gap:12px;flex:1;min-width:0}
.detail-header-left h2{font-size:18px;font-weight:700;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
.detail-header-left .source-badge{
  padding:3px 10px;border-radius:10px;font-size:11px;font-weight:600;
  background:rgba(159,122,234,0.15);color:var(--accent-purple);flex-shrink:0;
}
.detail-actions{display:flex;gap:8px}

/* Chat Area */
.chat-area{flex:1;display:flex;flex-direction:column;overflow:hidden}
.messages{
  flex:1;overflow-y:auto;padding:24px;
  display:flex;flex-direction:column;gap:16px;
}
.messages::-webkit-scrollbar{width:6px}
.messages::-webkit-scrollbar-thumb{background:var(--border);border-radius:4px}

.message{
  max-width:85%;padding:16px 20px;
  border-radius:var(--radius);
  font-size:14px;line-height:1.7;
  animation:fadeIn 0.3s ease;
}
@keyframes fadeIn{from{opacity:0;transform:translateY(8px)}to{opacity:1;transform:translateY(0)}}
.message.user{
  align-self:flex-end;
  background:linear-gradient(135deg,var(--accent-blue),var(--accent-purple));
  color:#fff;border-bottom-right-radius:4px;
}
.message.assistant{
  align-self:flex-start;
  background:var(--bg-card);
  border:1px solid var(--border);border-bottom-left-radius:4px;
}
.message pre{
  background:var(--bg-input);padding:12px;border-radius:var(--radius-xs);
  overflow-x:auto;margin:8px 0;font-size:13px;
}
.message .meta{font-size:11px;color:var(--text-muted);margin-top:8px}

.chat-welcome{
  flex:1;display:flex;flex-direction:column;align-items:center;justify-content:center;
  gap:12px;color:var(--text-muted);
}
.chat-welcome h3{font-size:20px;color:var(--text-secondary)}
.chat-welcome p{font-size:13px;max-width:500px;text-align:center;line-height:1.6}

/* Input Area */
.input-area{
  padding:16px 24px;border-top:1px solid var(--border);
  background:var(--bg-secondary);
}
.input-controls{
  display:flex;gap:10px;margin-bottom:12px;align-items:center;
}
.input-controls select,.input-controls input{
  padding:8px 12px;
  background:var(--bg-input);color:var(--text-primary);
  border:1px solid var(--border);border-radius:var(--radius-xs);
  font-size:13px;
}
.input-controls select{min-width:180px}
.input-controls select:focus,.input-controls input:focus{border-color:var(--accent-blue)}
.input-controls label{font-size:12px;color:var(--text-secondary);font-weight:500;white-space:nowrap}
.input-row{display:flex;gap:10px;align-items:flex-end}
.input-row textarea{
  flex:1;padding:12px 16px;
  background:var(--bg-input);color:var(--text-primary);
  border:1px solid var(--border);border-radius:var(--radius);
  font-size:14px;resize:none;
  min-height:48px;max-height:160px;
  line-height:1.5;
}
.input-row textarea:focus{border-color:var(--accent-blue)}
.send-btn{
  width:48px;height:48px;border-radius:var(--radius);
  background:linear-gradient(135deg,var(--accent),var(--accent-purple));
  color:#fff;display:flex;align-items:center;justify-content:center;
  transition:var(--transition);flex-shrink:0;
}
.send-btn:hover{opacity:0.9;transform:scale(1.05)}
.send-btn:disabled{opacity:0.4;cursor:not-allowed;transform:none}
.send-btn svg{width:20px;height:20px}
.toggle-stream{
  display:flex;align-items:center;gap:6px;font-size:12px;color:var(--text-secondary);cursor:pointer;
}
.toggle-stream input[type=checkbox]{accent-color:var(--accent-blue)}

/* Modal */
.modal-overlay{
  position:fixed;inset:0;background:rgba(0,0,0,0.6);
  display:flex;align-items:center;justify-content:center;
  z-index:1000;opacity:0;pointer-events:none;
  transition:opacity 0.2s ease;
  backdrop-filter:blur(4px);
}
.modal-overlay.active{opacity:1;pointer-events:all}
.modal{
  background:var(--bg-secondary);border:1px solid var(--border);
  border-radius:var(--radius);
  width:90%;max-width:640px;max-height:85vh;
  box-shadow:var(--shadow);
  display:flex;flex-direction:column;
  transform:scale(0.95);transition:transform 0.2s ease;
}
.modal-overlay.active .modal{transform:scale(1)}
.modal-header{
  padding:20px 24px;border-bottom:1px solid var(--border);
  display:flex;align-items:center;justify-content:space-between;
}
.modal-header h2{font-size:18px;font-weight:700}
.modal-close{
  width:32px;height:32px;border-radius:50%;
  background:var(--bg-hover);color:var(--text-secondary);
  display:flex;align-items:center;justify-content:center;
  font-size:18px;transition:var(--transition);
}
.modal-close:hover{background:var(--accent);color:#fff}
.modal-body{padding:24px;overflow-y:auto;flex:1}
.modal-footer{
  padding:16px 24px;border-top:1px solid var(--border);
  display:flex;justify-content:flex-end;gap:10px;
}
.form-group{margin-bottom:18px}
.form-group label{display:block;font-size:13px;font-weight:600;color:var(--text-secondary);margin-bottom:6px}
.form-group input,.form-group textarea,.form-group select{
  width:100%;padding:10px 14px;
  background:var(--bg-input);color:var(--text-primary);
  border:1px solid var(--border);border-radius:var(--radius-xs);
  font-size:14px;
}
.form-group textarea{resize:vertical;min-height:80px}
.form-group input:focus,.form-group textarea:focus{border-color:var(--accent-blue)}
.form-group .hint{font-size:11px;color:var(--text-muted);margin-top:4px}

/* Context items */
.context-list{display:flex;flex-direction:column;gap:10px}
.context-entry{
  background:var(--bg-input);border:1px solid var(--border);
  border-radius:var(--radius-xs);padding:12px;
  position:relative;
}
.context-entry textarea{margin-bottom:8px}
.context-entry input{margin-bottom:0}
.remove-context{
  position:absolute;top:8px;right:8px;
  width:24px;height:24px;border-radius:50%;
  background:var(--accent);color:#fff;
  font-size:14px;display:flex;align-items:center;justify-content:center;
  transition:var(--transition);
}
.remove-context:hover{background:var(--accent-hover)}
.add-context-btn{
  padding:8px;border:1px dashed var(--border);
  border-radius:var(--radius-xs);color:var(--text-muted);
  background:transparent;font-size:13px;
  transition:var(--transition);
}
.add-context-btn:hover{border-color:var(--accent-blue);color:var(--accent-blue)}

/* Context type selector */
.ctx-type-select{
  width:100%;padding:8px 10px;margin-bottom:10px;
  background:var(--bg-primary);color:var(--text-primary);
  border:1px solid var(--border);border-radius:var(--radius-xs);
  font-size:13px;cursor:pointer;
}
.ctx-type-select:focus{border-color:var(--accent-blue)}
.ctx-field-area{margin-top:4px}
.ctx-file-btn:hover{border-color:var(--accent-blue);color:var(--accent-blue);background:var(--bg-hover)}

/* Search within context */
.ctx-search-row{display:flex;gap:8px;margin-bottom:8px}
.ctx-search-row input{
  flex:1;padding:8px 10px;
  background:var(--bg-primary);color:var(--text-primary);
  border:1px solid var(--border);border-radius:var(--radius-xs);font-size:13px;
}
.ctx-search-row input:focus{border-color:var(--accent-blue)}
.ctx-search-btn{
  padding:6px 14px;border-radius:var(--radius-xs);
  background:var(--accent-blue);color:#fff;font-size:12px;font-weight:600;
  white-space:nowrap;transition:var(--transition);
}
.ctx-search-btn:hover{background:#3182ce}
.ctx-search-btn:disabled{opacity:0.5;cursor:not-allowed}

/* Search results dropdown */
.ctx-search-results{
  max-height:200px;overflow-y:auto;
  border:1px solid var(--border);border-radius:var(--radius-xs);
  margin-bottom:8px;
}
.ctx-search-results::-webkit-scrollbar{width:4px}
.ctx-search-results::-webkit-scrollbar-thumb{background:var(--border);border-radius:4px}
.ctx-search-result-item{
  padding:10px 12px;font-size:12px;line-height:1.5;
  color:var(--text-secondary);cursor:pointer;
  border-bottom:1px solid var(--border);
  transition:var(--transition);
}
.ctx-search-result-item:last-child{border-bottom:none}
.ctx-search-result-item:hover{background:var(--bg-hover);color:var(--text-primary)}
.ctx-search-result-item .result-lang{
  display:inline-block;padding:1px 6px;border-radius:8px;
  font-size:10px;font-weight:600;margin-right:6px;
  background:rgba(159,122,234,0.15);color:var(--accent-purple);
}
.ctx-search-no-results{
  padding:12px;text-align:center;font-size:12px;color:var(--text-muted);
}

/* Pecha capsule tags */
.pecha-tags{display:flex;flex-wrap:wrap;gap:6px;margin-top:8px}
.pecha-tag{
  display:inline-flex;align-items:center;gap:6px;
  padding:5px 12px;border-radius:16px;
  background:rgba(56,178,172,0.15);border:1px solid rgba(56,178,172,0.3);
  color:var(--accent-green);font-size:12px;font-weight:500;
  animation:fadeIn 0.3s ease;
}
.pecha-tag .pecha-tag-remove{
  width:16px;height:16px;border-radius:50%;
  background:rgba(56,178,172,0.3);color:var(--accent-green);
  display:flex;align-items:center;justify-content:center;
  font-size:11px;cursor:pointer;transition:var(--transition);
  border:none;padding:0;line-height:1;
}
.pecha-tag .pecha-tag-remove:hover{background:var(--accent);color:#fff}

/* Checkbox */
.checkbox-group{display:flex;align-items:center;gap:8px;margin-bottom:18px}
.checkbox-group input[type=checkbox]{accent-color:var(--accent-blue);width:16px;height:16px}
.checkbox-group label{font-size:13px;color:var(--text-secondary);margin:0}

/* Loading */
.spinner{
  width:20px;height:20px;border:2px solid var(--border);
  border-top-color:var(--accent-blue);border-radius:50%;
  animation:spin 0.6s linear infinite;display:inline-block;
}
@keyframes spin{to{transform:rotate(360deg)}}

.loading-dots::after{
  content:'';animation:dots 1.5s steps(4,end) infinite;
}
@keyframes dots{
  0%{content:''}25%{content:'.'}50%{content:'..'}75%{content:'...'}
}

/* Toast */
.toast-container{position:fixed;top:20px;right:20px;z-index:2000;display:flex;flex-direction:column;gap:8px}
.toast{
  padding:12px 20px;border-radius:var(--radius-xs);
  font-size:13px;font-weight:500;
  box-shadow:var(--shadow);
  animation:slideIn 0.3s ease;
  max-width:400px;
}
@keyframes slideIn{from{opacity:0;transform:translateX(40px)}to{opacity:1;transform:translateX(0)}}
.toast.success{background:#38a169;color:#fff}
.toast.error{background:#e53e3e;color:#fff}
.toast.info{background:var(--accent-blue);color:#fff}

/* Details panel */
.details-panel{
  padding:24px;overflow-y:auto;border-bottom:1px solid var(--border);
  background:var(--bg-primary);max-height:250px;
  display:none;
}
.details-panel.visible{display:block}
.details-panel h4{font-size:13px;color:var(--text-muted);text-transform:uppercase;letter-spacing:0.5px;margin-bottom:8px}
.details-panel .detail-row{
  display:flex;gap:12px;margin-bottom:6px;font-size:13px;
}
.details-panel .detail-row .label{color:var(--text-muted);min-width:110px}
.details-panel .detail-row .value{color:var(--text-primary)}
.system-prompt-preview{
  background:var(--bg-input);padding:12px;border-radius:var(--radius-xs);
  font-size:13px;color:var(--text-secondary);
  max-height:80px;overflow-y:auto;margin-top:8px;
  white-space:pre-wrap;line-height:1.5;
}
.context-chips{display:flex;flex-wrap:wrap;gap:6px;margin-top:8px}
.context-chip{
  padding:4px 10px;background:rgba(66,153,225,0.1);
  border:1px solid rgba(66,153,225,0.2);border-radius:10px;
  font-size:11px;color:var(--accent-blue);
}
.toggle-details{
  font-size:12px;color:var(--accent-blue);background:none;
  text-decoration:underline;padding:0;
}
</style>
</head>
<body>
<div class="app">
  <!-- Sidebar -->
  <div class="sidebar">
    <div class="sidebar-header">
      <h1> Assistant Agent</h1>
      <div class="token-section">
        <label>Authentication</label>
        <button class="btn-sm btn-google" onclick="loginWithGoogle()" id="googleLoginBtn" style="width:100%;margin-bottom:12px;background:#4285f4;color:#fff;display:flex;align-items:center;justify-content:center;gap:8px;padding:10px">
          <svg width="18" height="18" viewBox="0 0 18 18" fill="none" xmlns="http://www.w3.org/2000/svg">
            <path d="M17.64 9.2c0-.637-.057-1.251-.164-1.84H9v3.481h4.844c-.209 1.125-.843 2.078-1.796 2.717v2.258h2.908c1.702-1.567 2.684-3.874 2.684-6.615z" fill="#4285F4"/>
            <path d="M9.003 18c2.43 0 4.467-.806 5.956-2.184l-2.908-2.258c-.806.54-1.837.86-3.048.86-2.344 0-4.328-1.584-5.036-3.711H.957v2.332C2.438 15.983 5.482 18 9.003 18z" fill="#34A853"/>
            <path d="M3.964 10.71c-.18-.54-.282-1.117-.282-1.71 0-.593.102-1.17.282-1.71V4.958H.957C.347 6.173 0 7.548 0 9c0 1.452.348 2.827.957 4.042l3.007-2.332z" fill="#FBBC05"/>
            <path d="M9.003 3.58c1.321 0 2.508.454 3.44 1.345l2.582-2.58C13.464.891 11.426 0 9.003 0 5.482 0 2.438 2.017.957 4.958L3.964 7.29c.708-2.127 2.692-3.71 5.036-3.71z" fill="#EA4335"/>
          </svg>
          Get Token
        </button>
        <div class="token-input">
          <input type="password" id="tokenInput" placeholder="Token will appear after login..." readonly style="background:var(--bg-primary);cursor:not-allowed"/>
          <button class="btn-sm btn-outline" onclick="toggleTokenVisibility()" id="toggleTokenBtn">Show</button>
        </div>
      </div>
    </div>
    <button class="new-assistant-btn" onclick="openCreateModal()">+ New Assistant</button>
    <div class="assistant-list" id="assistantList"></div>
    <div class="sidebar-footer">
      Powered by LangGraph + FastAPI
    </div>
  </div>

  <!-- Main -->
  <div class="main" id="mainArea">
    <div class="empty-state" id="emptyState">
      <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
        <path d="M20 7H4a2 2 0 00-2 2v10a2 2 0 002 2h16a2 2 0 002-2V9a2 2 0 00-2-2z"/>
        <path d="M16 7V5a4 4 0 00-8 0v2"/>
        <circle cx="12" cy="14" r="2"/>
      </svg>
      <h2>Welcome to Assistant Agent</h2>
      <p>Create or select an assistant from the sidebar to start chatting. Each assistant has its own system prompt, context, and configuration.</p>
    </div>

    <!-- Active Assistant View -->
    <div id="assistantView" style="display:none;flex:1;flex-direction:column;overflow:hidden">
      <div class="detail-header">
        <div class="detail-header-left">
          <h2 id="activeAssistantName"></h2>
          <span class="source-badge" id="activeAssistantSource"></span>
          <button class="toggle-details" onclick="toggleDetails()">Details</button>
        </div>
        <div class="detail-actions">
          <button class="btn-sm btn-outline" onclick="openEditModal()">Edit</button>
          <button class="btn-sm btn-danger" onclick="deleteCurrentAssistant()">Delete</button>
        </div>
      </div>

      <div class="details-panel" id="detailsPanel">
        <h4>Assistant Details</h4>
        <div class="detail-row"><span class="label">ID</span><span class="value" id="detailId"></span></div>
        <div class="detail-row"><span class="label">Description</span><span class="value" id="detailDesc"></span></div>
        <div class="detail-row"><span class="label">Created By</span><span class="value" id="detailCreatedBy"></span></div>
        <div class="detail-row"><span class="label">System Assist</span><span class="value" id="detailSysAssist"></span></div>
        <h4 style="margin-top:12px">System Prompt</h4>
        <div class="system-prompt-preview" id="detailSystemPrompt"></div>
        <h4 style="margin-top:12px">Contexts</h4>
        <div class="context-chips" id="detailContexts"></div>
      </div>

      <div class="chat-area">
        <div class="messages" id="messagesContainer">
          <div class="chat-welcome" id="chatWelcome">
            <h3>Start a conversation</h3>
            <p>Send a prompt to this assistant. Choose a model and optionally set a target language below.</p>
          </div>
        </div>

        <div class="input-area">
          <div class="input-controls">
            <label>Model</label>
            <select id="modelSelect">
              <optgroup label="Anthropic">
                <option value="claude-sonnet-4-20250514">Claude Sonnet 4.0</option>
                <option value="claude-3-5-haiku-20241022">Claude 3.5 Haiku</option>
                <option value="claude-3-opus-20240229">Claude 3 Opus</option>
                <option value="claude-haiku-4-5-20251001">Claude Haiku 4.5</option>
                <option value="claude-sonnet-4-5-20250929">Claude Sonnet 4.5</option>
              </optgroup>
              <optgroup label="OpenAI">
                <option value="gpt-4">GPT-4</option>
                <option value="gpt-4-turbo">GPT-4 Turbo</option>
                <option value="gpt-3.5-turbo">GPT-3.5 Turbo</option>
              </optgroup>
              <optgroup label="Google">
                <option value="gemini-2.5-pro">Gemini 2.5 Pro</option>
                <option value="gemini-2.5-flash">Gemini 2.5 Flash</option>
                <option value="gemini-2.5-flash-thinking">Gemini 2.5 Flash Thinking</option>
                <option value="gemini-pro-vision">Gemini Pro Vision</option>
                <option value="gemini-pro">Gemini Pro</option>
              </optgroup>
              <optgroup label="Dharmamitra">
                <option value="dharamitra">Dharmamitra</option>
              </optgroup>
            </select>
            <label>Target Language</label>
            <input type="text" id="targetLang" placeholder="e.g. English, Tibetan..." style="width:160px"/>
            <label class="toggle-stream">
              <input type="checkbox" id="streamToggle" checked/> Stream
            </label>
          </div>
          <div class="input-row">
            <textarea id="promptInput" placeholder="Type your message... (Shift+Enter for newline)" rows="1"
              onkeydown="handleInputKeydown(event)" oninput="autoResize(this)"></textarea>
            <button class="send-btn" id="sendBtn" onclick="sendMessage()" disabled>
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M22 2L11 13"/><path d="M22 2L15 22L11 13L2 9L22 2Z"/></svg>
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</div>

<!-- Modal -->
<div class="modal-overlay" id="modalOverlay" onclick="closeModal(event)">
  <div class="modal" onclick="event.stopPropagation()">
    <div class="modal-header">
      <h2 id="modalTitle">New Assistant</h2>
      <button class="modal-close" onclick="closeModal()">&times;</button>
    </div>
    <div class="modal-body">
      <div class="form-group">
        <label>Name *</label>
        <input type="text" id="formName" placeholder="My Translation Assistant"/>
      </div>
      <div class="form-group">
        <label>Description</label>
        <textarea id="formDescription" placeholder="What does this assistant do?" rows="2"></textarea>
      </div>
      <div class="form-group">
        <label>Source Type</label>
        <input type="text" id="formSourceType" placeholder="e.g. translation, summarization..."/>
      </div>
      <div class="form-group">
        <label>System Prompt *</label>
        <textarea id="formSystemPrompt" placeholder="You are a helpful translation assistant..." rows="4"></textarea>
      </div>
      <div class="checkbox-group">
        <input type="checkbox" id="formSystemAssistance"/>
        <label for="formSystemAssistance">System Assistance</label>
      </div>
      <div class="form-group">
        <label>Contexts</label>
        <div class="hint" style="margin-bottom:8px">Select a context type to add.</div>
        <select class="ctx-type-select" id="globalContextTypeSelect" onchange="addContextFromGlobal()" style="margin-bottom:12px">
          <option value="">-- Select context type --</option>
          <option value="content">Content</option>
          <option value="file">File URL</option>
          <option value="search">Search Pecha</option>
        </select>
        <div class="context-list" id="contextList"></div>
      </div>
    </div>
    <div class="modal-footer">
      <button class="btn-sm btn-outline" onclick="closeModal()">Cancel</button>
      <button class="btn-sm btn-primary" id="modalSubmitBtn" onclick="submitModal()">Create</button>
    </div>
  </div>
</div>

<!-- Toast -->
<div class="toast-container" id="toastContainer"></div>

<script>
const API_BASE = '';
let AUTH0_DOMAIN = '';
let AUTH0_CLIENT_ID = '';
const AUTH0_REDIRECT_URI = window.location.origin + '/';
let AUTH0_AUDIENCE = '';

let assistants = [];
let activeAssistant = null;
let editingId = null;
let chatHistories = {};
let isSending = false;

// Load Auth0 configuration
async function loadAuth0Config() {
  try {
    const r = await fetch(API_BASE + '/config');
    if (r.ok) {
      const config = await r.json();
      AUTH0_DOMAIN = config.auth0_domain;
      AUTH0_CLIENT_ID = config.auth0_client_id;
      AUTH0_AUDIENCE = `https://${AUTH0_DOMAIN}/api/v2/`;
    }
  } catch(e) {
    console.error('Failed to load Auth0 config', e);
  }
}

// Auth0 Google Login
function loginWithGoogle() {
  if (!AUTH0_DOMAIN || !AUTH0_CLIENT_ID) {
    toast('Auth0 configuration not loaded. Please refresh the page.', 'error');
    return;
  }
  
  const state = generateRandomString(32);
  const nonce = generateRandomString(32);
  sessionStorage.setItem('auth0_state', state);
  sessionStorage.setItem('auth0_nonce', nonce);
  
  const authUrl = `https://${AUTH0_DOMAIN}/authorize?` +
    `response_type=id_token&` +
    `client_id=${AUTH0_CLIENT_ID}&` +
    `redirect_uri=${encodeURIComponent(AUTH0_REDIRECT_URI)}&` +
    `scope=openid profile email&` +
    `connection=google-oauth2&` +
    `state=${state}&` +
    `nonce=${nonce}`;
  
  window.location.href = authUrl;
}

function generateRandomString(length) {
  const chars = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789';
  let result = '';
  for (let i = 0; i < length; i++) {
    result += chars.charAt(Math.floor(Math.random() * chars.length));
  }
  return result;
}

function handleAuthCallback() {
  const hash = window.location.hash.substring(1);
  if (!hash) return;
  
  const params = new URLSearchParams(hash);
  const idToken = params.get('id_token');
  const state = params.get('state');
  const error = params.get('error');
  
  if (error) {
    toast('Login failed: ' + (params.get('error_description') || error), 'error');
    window.history.replaceState({}, document.title, window.location.pathname);
    return;
  }
  
  const savedState = sessionStorage.getItem('auth0_state');
  
  if (idToken && state === savedState) {
    // Use the ID token for API authentication
    document.getElementById('tokenInput').value = idToken;
    document.getElementById('tokenInput').readOnly = false;
    document.getElementById('tokenInput').style.cursor = 'text';
    document.getElementById('tokenInput').style.background = 'var(--bg-input)';
    
    sessionStorage.removeItem('auth0_state');
    sessionStorage.removeItem('auth0_nonce');
    
    // Clear the hash from URL
    window.history.replaceState({}, document.title, window.location.pathname);
    
    toast('Successfully logged in with Google!', 'success');
    
    // Store user info
    try {
      const base64Url = idToken.split('.')[1];
      const base64 = base64Url.replace(/-/g, '+').replace(/_/g, '/');
      const payload = JSON.parse(window.atob(base64));
      sessionStorage.setItem('user_email', payload.email || '');
      sessionStorage.setItem('user_name', payload.name || '');
    } catch(e) {
      console.error('Failed to parse token', e);
    }
    
    // Auto-load assistants
    loadAssistants();
  }
}

function getToken() {
  return document.getElementById('tokenInput').value.trim();
}

function authHeaders() {
  const t = getToken();
  const h = {'Content-Type':'application/json'};
  if (t) h['Authorization'] = 'Bearer ' + t;
  return h;
}

function toast(msg, type='info') {
  const c = document.getElementById('toastContainer');
  const d = document.createElement('div');
  d.className = 'toast ' + type;
  d.textContent = msg;
  c.appendChild(d);
  setTimeout(() => { d.style.opacity='0'; d.style.transform='translateX(40px)'; setTimeout(()=>d.remove(),300) }, 3500);
}

function toggleTokenVisibility() {
  const inp = document.getElementById('tokenInput');
  const btn = document.getElementById('toggleTokenBtn');
  if (inp.type === 'password') { inp.type='text'; btn.textContent='Hide'; }
  else { inp.type='password'; btn.textContent='Show'; }
}

// Assistants
async function loadAssistants() {
  try {
    const r = await fetch(API_BASE + '/assistant?skip=0&limit=100', {headers: authHeaders()});
    if (!r.ok) throw new Error('Failed to load');
    const data = await r.json();
    assistants = data.assistants || [];
    renderAssistantList();
  } catch(e) {
    assistants = [];
    renderAssistantList();
  }
}

function renderAssistantList() {
  const list = document.getElementById('assistantList');
  if (!assistants.length) {
    list.innerHTML = '<div style="padding:20px;text-align:center;color:var(--text-muted);font-size:13px">No assistants yet.<br/>Create one to get started.</div>';
    return;
  }
  list.innerHTML = assistants.map(a => `
    <div class="assistant-item ${activeAssistant && activeAssistant.id === a.id ? 'active' : ''}"
         onclick="selectAssistant('${a.id}')">
      <h3>${esc(a.name)}</h3>
      <p>${esc(a.description || 'No description')}</p>
      ${a.source_type ? `<span class="badge">${esc(a.source_type)}</span>` : ''}
    </div>
  `).join('');
}

async function selectAssistant(id) {
  const token = getToken();
  if (!token) { toast('Please enter a bearer token first','error'); return; }
  try {
    const r = await fetch(API_BASE + '/assistant/' + id, {headers: authHeaders()});
    if (!r.ok) throw new Error('Failed to load assistant');
    activeAssistant = await r.json();
    renderAssistantList();
    showAssistantView();
  } catch(e) {
    toast('Error loading assistant: ' + e.message, 'error');
  }
}

function showAssistantView() {
  document.getElementById('emptyState').style.display = 'none';
  const v = document.getElementById('assistantView');
  v.style.display = 'flex';
  document.getElementById('activeAssistantName').textContent = activeAssistant.name;
  document.getElementById('activeAssistantSource').textContent = activeAssistant.source_type || 'general';
  document.getElementById('detailId').textContent = activeAssistant.id;
  document.getElementById('detailDesc').textContent = activeAssistant.description || '—';
  document.getElementById('detailCreatedBy').textContent = activeAssistant.created_by || '—';
  document.getElementById('detailSysAssist').textContent = activeAssistant.system_assistance ? 'Yes' : 'No';
  document.getElementById('detailSystemPrompt').textContent = activeAssistant.system_prompt;
  const ctxDiv = document.getElementById('detailContexts');
  if (activeAssistant.contexts && activeAssistant.contexts.length) {
    ctxDiv.innerHTML = activeAssistant.contexts.map((c,i) => {
      if (c.pecha_title) return `<span class="context-chip">Pecha: ${esc(c.pecha_title)}</span>`;
      if (c.content) return `<span class="context-chip">Text #${i+1}</span>`;
      if (c.file_url) return `<span class="context-chip">File: ${esc(c.file_url)}</span>`;
      return `<span class="context-chip">Context #${i+1}</span>`;
    }).join('');
  } else {
    ctxDiv.innerHTML = '<span style="font-size:12px;color:var(--text-muted)">No contexts</span>';
  }
  document.getElementById('detailsPanel').classList.remove('visible');
  renderMessages();
}

function toggleDetails() {
  document.getElementById('detailsPanel').classList.toggle('visible');
}

// Create / Edit Modal
function openCreateModal() {
  editingId = null;
  document.getElementById('modalTitle').textContent = 'New Assistant';
  document.getElementById('modalSubmitBtn').textContent = 'Create';
  clearForm();
  document.getElementById('modalOverlay').classList.add('active');
}

function openEditModal() {
  if (!activeAssistant) return;
  editingId = activeAssistant.id;
  document.getElementById('modalTitle').textContent = 'Edit Assistant';
  document.getElementById('modalSubmitBtn').textContent = 'Save Changes';
  document.getElementById('formName').value = activeAssistant.name || '';
  document.getElementById('formDescription').value = activeAssistant.description || '';
  document.getElementById('formSourceType').value = activeAssistant.source_type || '';
  document.getElementById('formSystemPrompt').value = activeAssistant.system_prompt || '';
  document.getElementById('formSystemAssistance').checked = activeAssistant.system_assistance || false;
  const cl = document.getElementById('contextList');
  cl.innerHTML = '';
  if (activeAssistant.contexts && activeAssistant.contexts.length) {
    activeAssistant.contexts.forEach(c => {
      let type = 'content';
      if (c.pecha_text_id) type = 'search';
      else if (c.file_url) type = 'file';
      addContextEntry(type, {content: c.content, file_url: c.file_url, pecha_title: c.pecha_title, pecha_text_id: c.pecha_text_id});
    });
  }
  document.getElementById('modalOverlay').classList.add('active');
}

function closeModal(e) {
  if (e && e.target !== document.getElementById('modalOverlay')) return;
  document.getElementById('modalOverlay').classList.remove('active');
}

function clearForm() {
  document.getElementById('formName').value = '';
  document.getElementById('formDescription').value = '';
  document.getElementById('formSourceType').value = '';
  document.getElementById('formSystemPrompt').value = '';
  document.getElementById('formSystemAssistance').checked = false;
  document.getElementById('contextList').innerHTML = '';
}

function addContextFromGlobal() {
  const globalSelect = document.getElementById('globalContextTypeSelect');
  const type = globalSelect.value;
  if (!type) return;
  
  addContextEntry(type, {});
  
  // Reset the global dropdown
  globalSelect.value = '';
}

function addContextEntry(type='content', data={}) {
  const cl = document.getElementById('contextList');
  const div = document.createElement('div');
  div.className = 'context-entry';
  const entryId = 'ctx_' + Date.now() + '_' + Math.random().toString(36).slice(2,7);
  div.setAttribute('data-entry-id', entryId);
  div.setAttribute('data-context-type', type);

  let selectedType = type;
  if (data.pecha_text_id) selectedType = 'search';
  else if (data.file_url) selectedType = 'file';
  else if (data.content) selectedType = 'content';

  // Store type as data attribute for retrieval
  div.setAttribute('data-context-type', selectedType);

  // Add type label and remove button only
  let typeLabel = 'Content';
  if (selectedType === 'file') typeLabel = 'File URL';
  else if (selectedType === 'search') typeLabel = 'Search Pecha';

  div.innerHTML = `
    <button class="remove-context" onclick="this.parentElement.remove()">&times;</button>
    <div style="font-size:11px;font-weight:600;color:var(--text-muted);margin-bottom:8px;text-transform:uppercase;letter-spacing:0.5px">${typeLabel}</div>
    <div class="ctx-field-area"></div>
  `;
  cl.appendChild(div);

  const fieldArea = div.querySelector('.ctx-field-area');
  if (selectedType === 'content') {
    renderContentField(fieldArea, data.content || '');
  } else if (selectedType === 'file') {
    renderFileField(fieldArea, data.file_url || '');
  } else if (selectedType === 'search') {
    renderSearchField(fieldArea, data.pecha_title || '', data.pecha_text_id || '');
  }
}

function renderContentField(container, value) {
  container.innerHTML = `
    <textarea placeholder="Context content..." rows="3" class="ctx-content" style="width:100%;padding:8px 10px;background:var(--bg-primary);color:var(--text-primary);border:1px solid var(--border);border-radius:var(--radius-xs);font-size:13px">${esc(value)}</textarea>
  `;
}

function renderFileField(container, value) {
  const hasFile = value && value.trim();
  container.innerHTML = `
    <div style="display:flex;flex-direction:column;gap:8px">
      ${hasFile ? `
        <div style="padding:8px 10px;background:var(--bg-tertiary);border:1px solid var(--border);border-radius:var(--radius-xs);font-size:12px;display:flex;align-items:center;justify-content:space-between">
          <span style="color:var(--accent-green);font-weight:500">✓ File uploaded</span>
          <button class="btn-sm btn-danger" onclick="clearUploadedFile(this)" style="padding:4px 10px;font-size:11px">Remove</button>
        </div>
      ` : `
        <div style="position:relative">
          <input type="file" class="ctx-file-input" accept=".pdf,.docx,.txt,.doc" onchange="handleFileSelect(this)" style="display:none"/>
          <button class="ctx-file-btn" onclick="this.previousElementSibling.click()" style="width:100%;padding:10px;background:var(--bg-input);color:var(--text-secondary);border:1px dashed var(--border);border-radius:var(--radius-xs);font-size:13px;cursor:pointer;transition:var(--transition)">
            Choose file (.pdf, .docx, .txt, .doc)
          </button>
        </div>
        <div class="ctx-file-status" style="font-size:11px;color:var(--text-muted);min-height:16px"></div>
      `}
      <input type="hidden" class="ctx-file-url" value="${esc(value)}"/>
    </div>
  `;
}

async function handleFileSelect(inputEl) {
  const file = inputEl.files?.[0];
  if (!file) return;

  const token = getToken();
  if (!token) {
    toast('Please enter a bearer token first', 'error');
    inputEl.value = '';
    return;
  }

  const entry = inputEl.closest('.context-entry');
  const statusDiv = entry.querySelector('.ctx-file-status');
  const fileBtn = entry.querySelector('.ctx-file-btn');
  const hiddenUrlInput = entry.querySelector('.ctx-file-url');

  // Show uploading status
  if (statusDiv) statusDiv.innerHTML = '<span class="spinner" style="width:12px;height:12px;border-width:2px"></span> Uploading...';
  if (fileBtn) fileBtn.disabled = true;

  try {
    const formData = new FormData();
    formData.append('file', file);

    const r = await fetch(API_BASE + '/media/upload', {
      method: 'POST',
      headers: {
        'Authorization': 'Bearer ' + token
      },
      body: formData
    });

    if (!r.ok) {
      const err = await r.json().catch(() => ({}));
      throw new Error(err.detail?.message || err.detail || 'Upload failed');
    }

    const data = await r.json();
    
    // Store the S3 key (not the temporary presigned URL)
    hiddenUrlInput.value = data.key;

    // Re-render the field to show success state
    const fieldArea = entry.querySelector('.ctx-field-area');
    renderFileField(fieldArea, data.key);

    toast('File uploaded successfully!', 'success');
  } catch (e) {
    if (statusDiv) statusDiv.innerHTML = '<span style="color:#fc8181">Upload failed: ' + esc(e.message) + '</span>';
    if (fileBtn) fileBtn.disabled = false;
    toast('Upload error: ' + e.message, 'error');
    inputEl.value = '';
  }
}

function clearUploadedFile(btn) {
  const entry = btn.closest('.context-entry');
  const fieldArea = entry.querySelector('.ctx-field-area');
  renderFileField(fieldArea, '');
}

function renderSearchField(container, title, textId) {
  container.innerHTML = `
    <div class="ctx-search-row">
      <input type="text" class="ctx-search-input" placeholder="Search Buddhist texts..." onkeydown="if(event.key==='Enter'){event.preventDefault();doContextSearch(this)}"/>
      <button class="ctx-search-btn" onclick="doContextSearch(this.previousElementSibling)">Search</button>
    </div>
    <div class="ctx-search-results" style="display:none"></div>
    <div class="pecha-tags"></div>
    <input type="hidden" class="ctx-pecha-title" value="${esc(title)}"/>
    <input type="hidden" class="ctx-pecha-text-id" value="${esc(textId)}"/>
  `;
  if (title && textId) {
    const tagsDiv = container.querySelector('.pecha-tags');
    addPechaTag(tagsDiv, container, title, textId);
  }
}

let _searchResultsCache = {};

async function doContextSearch(inputEl) {
  const query = inputEl.value.trim();
  if (!query) return;
  const entry = inputEl.closest('.context-entry');
  const resultsDiv = entry.querySelector('.ctx-search-results');
  const btn = entry.querySelector('.ctx-search-btn');
  btn.disabled = true;
  btn.textContent = 'Searching...';
  resultsDiv.style.display = 'block';
  resultsDiv.innerHTML = '<div class="ctx-search-no-results"><span class="spinner"></span> Searching...</div>';

  try {
    const r = await fetch('https://search.buddhistai.tools/search', {
      method: 'POST',
      headers: {'Content-Type':'application/json'},
      body: JSON.stringify({limit:10, query:query, return_text:true, search_type:'exact'})
    });
    if (!r.ok) throw new Error('Search failed');
    const data = await r.json();
    const results = data.results || [];
    if (!results.length) {
      resultsDiv.innerHTML = '<div class="ctx-search-no-results">No results found</div>';
    } else {
      results.forEach(item => { _searchResultsCache[item.id] = item.entity?.text || ''; });
      resultsDiv.innerHTML = results.map(item => {
        const text = item.entity?.text || '';
        const lang = item.entity?.language || '';
        const displayText = text.length > 150 ? text.slice(0,150) + '...' : text;
        return '<div class="ctx-search-result-item" data-result-id="' + esc(item.id) + '" onclick="selectSearchResult(this)">'
          + '<span class="result-lang">' + esc(lang) + '</span>' + esc(displayText)
          + '</div>';
      }).join('');
    }
  } catch(e) {
    resultsDiv.innerHTML = '<div class="ctx-search-no-results" style="color:#fc8181">Search error: ' + esc(e.message) + '</div>';
  } finally {
    btn.disabled = false;
    btn.textContent = 'Search';
  }
}

function selectSearchResult(el) {
  const id = el.getAttribute('data-result-id');
  const fullText = _searchResultsCache[id] || '';
  const entry = el.closest('.context-entry');
  const fieldArea = entry.querySelector('.ctx-field-area');
  const tagsDiv = fieldArea.querySelector('.pecha-tags');
  const titleInput = fieldArea.querySelector('.ctx-pecha-title');
  const idInput = fieldArea.querySelector('.ctx-pecha-text-id');
  const resultsDiv = entry.querySelector('.ctx-search-results');

  const displayTitle = fullText.length > 80 ? fullText.slice(0,80) + '...' : fullText;
  titleInput.value = displayTitle;
  idInput.value = id;
  resultsDiv.style.display = 'none';

  tagsDiv.innerHTML = '';
  addPechaTag(tagsDiv, fieldArea, displayTitle, id);
}

function addPechaTag(tagsDiv, fieldArea, title, id) {
  const tag = document.createElement('span');
  tag.className = 'pecha-tag';
  tag.innerHTML = `<span class="pecha-tag-text">${esc(title)}</span><button class="pecha-tag-remove" onclick="removePechaTag(this)">&times;</button>`;
  tagsDiv.appendChild(tag);
}

function removePechaTag(btn) {
  const entry = btn.closest('.context-entry');
  const fieldArea = entry.querySelector('.ctx-field-area');
  fieldArea.querySelector('.ctx-pecha-title').value = '';
  fieldArea.querySelector('.ctx-pecha-text-id').value = '';
  btn.closest('.pecha-tag').remove();
}

function getContextsFromForm() {
  const entries = document.querySelectorAll('#contextList .context-entry');
  const contexts = [];
  entries.forEach(e => {
    const type = e.getAttribute('data-context-type');
    if (type === 'content') {
      const content = e.querySelector('.ctx-content')?.value.trim();
      if (content) contexts.push({content, file_url:null, pecha_title:null, pecha_text_id:null});
    } else if (type === 'file') {
      const file_url = e.querySelector('.ctx-file-url')?.value.trim();
      if (file_url) contexts.push({content:null, file_url, pecha_title:null, pecha_text_id:null});
    } else if (type === 'search') {
      const pecha_title = e.querySelector('.ctx-pecha-title')?.value.trim();
      const pecha_text_id = e.querySelector('.ctx-pecha-text-id')?.value.trim();
      if (pecha_title && pecha_text_id) contexts.push({content:null, file_url:null, pecha_title, pecha_text_id});
    }
  });
  return contexts;
}

async function submitModal() {
  const token = getToken();
  if (!token) { toast('Please enter a bearer token','error'); return; }
  const name = document.getElementById('formName').value.trim();
  const system_prompt = document.getElementById('formSystemPrompt').value.trim();
  if (!name || !system_prompt) { toast('Name and System Prompt are required','error'); return; }

  const body = {
    name,
    description: document.getElementById('formDescription').value.trim() || null,
    source_type: document.getElementById('formSourceType').value.trim() || null,
    system_prompt,
    system_assistance: document.getElementById('formSystemAssistance').checked,
    contexts: getContextsFromForm()
  };

  try {
    let r;
    if (editingId) {
      r = await fetch(API_BASE + '/assistant/' + editingId, {method:'PUT', headers:authHeaders(), body:JSON.stringify(body)});
    } else {
      r = await fetch(API_BASE + '/assistant', {method:'POST', headers:authHeaders(), body:JSON.stringify(body)});
    }
    if (!r.ok) { const err = await r.json().catch(()=>({})); throw new Error(err.detail?.message || 'Request failed'); }
    toast(editingId ? 'Assistant updated!' : 'Assistant created!', 'success');
    closeModal();
    await loadAssistants();
    if (editingId) await selectAssistant(editingId);
  } catch(e) {
    toast('Error: ' + e.message, 'error');
  }
}

async function deleteCurrentAssistant() {
  if (!activeAssistant) return;
  if (!confirm('Delete "' + activeAssistant.name + '"? This cannot be undone.')) return;
  const token = getToken();
  if (!token) { toast('Please enter a bearer token','error'); return; }
  try {
    const r = await fetch(API_BASE + '/assistant/' + activeAssistant.id, {method:'DELETE', headers:authHeaders()});
    if (!r.ok && r.status !== 204) throw new Error('Failed to delete');
    toast('Assistant deleted', 'success');
    delete chatHistories[activeAssistant.id];
    activeAssistant = null;
    document.getElementById('assistantView').style.display = 'none';
    document.getElementById('emptyState').style.display = 'flex';
    await loadAssistants();
  } catch(e) {
    toast('Error: ' + e.message, 'error');
  }
}

// Chat
function renderMessages() {
  const container = document.getElementById('messagesContainer');
  const history = chatHistories[activeAssistant.id] || [];
  if (!history.length) {
    container.innerHTML = `<div class="chat-welcome" id="chatWelcome">
      <h3>Start a conversation</h3>
      <p>Send a prompt to this assistant. Choose a model and optionally set a target language below.</p>
    </div>`;
    return;
  }
  container.innerHTML = history.map(m => {
    if (m.role === 'user') {
      return `<div class="message user">${esc(m.content)}</div>`;
    } else {
      return `<div class="message assistant">${formatAssistantMessage(m)}</div>`;
    }
  }).join('');
  container.scrollTop = container.scrollHeight;
}

function updateLastMessage() {
  const container = document.getElementById('messagesContainer');
  const lastEl = container.lastElementChild;
  if (!lastEl) return;
  const history = chatHistories[activeAssistant.id] || [];
  const lastMsg = history[history.length - 1];
  if (!lastMsg || lastMsg.role === 'user') return;
  lastEl.innerHTML = formatAssistantMessage(lastMsg);
  const isNearBottom = (container.scrollHeight - container.scrollTop - container.clientHeight) < 100;
  if (isNearBottom) container.scrollTop = container.scrollHeight;
}

function formatAssistantMessage(m) {
  let html = '';
  if (m.results && m.results.length) {
    m.results.forEach(r => {
      html += `<div style="margin-bottom:12px">`;
      html += `<div style="padding:8px 12px;background:var(--bg-input);border-radius:6px;font-size:13px">${esc(r.output_text)}</div>`;
      html += `</div>`;
    });
  }
  if (m.metadata) {
    html += `<div class="meta">Batches: ${m.metadata.total_batches} | Time: ${m.metadata.total_processing_time?.toFixed(2)}s</div>`;
  }
  if (m.streamContent) {
    html += `<div style="white-space:pre-wrap">${esc(m.streamContent)}</div>`;
  }
  if (m.errors && m.errors.length) {
    html += `<div style="color:#fc8181;margin-top:8px;font-size:13px">Errors: ${esc(JSON.stringify(m.errors))}</div>`;
  }
  if (m.error) {
    html += `<div style="color:#fc8181">${esc(m.error)}</div>`;
  }
  return html || '<span style="color:var(--text-muted)">Empty response</span>';
}

function handleInputKeydown(e) {
  if (e.key === 'Enter' && !e.shiftKey) {
    e.preventDefault();
    if (!isSending) sendMessage();
  }
}

function autoResize(el) {
  el.style.height = 'auto';
  el.style.height = Math.min(el.scrollHeight, 160) + 'px';
  document.getElementById('sendBtn').disabled = !el.value.trim();
}

async function sendMessage() {
  if (isSending || !activeAssistant) return;
  const input = document.getElementById('promptInput');
  const text = input.value.trim();
  if (!text) return;
  const token = getToken();
  if (!token) { toast('Please enter a bearer token','error'); return; }

  const model = document.getElementById('modelSelect').value;
  const targetLang = document.getElementById('targetLang').value.trim() || null;
  const useStream = document.getElementById('streamToggle').checked;

  if (!chatHistories[activeAssistant.id]) chatHistories[activeAssistant.id] = [];
  chatHistories[activeAssistant.id].push({role:'user', content:text});

  input.value = '';
  input.style.height = 'auto';
  document.getElementById('sendBtn').disabled = true;
  isSending = true;
  renderMessages();

  const prompts = text.split('\\n').filter(l => l.trim());

  const payload = {
    assistant_id: activeAssistant.id,
    prompt: prompts,
    model: model,
    target_language: targetLang
  };

  if (useStream) {
    await sendStream(payload);
  } else {
    await sendNormal(payload);
  }
  isSending = false;
}

async function sendNormal(payload) {
  const loadingMsg = {role:'assistant', streamContent:'Thinking...'};
  chatHistories[activeAssistant.id].push(loadingMsg);
  renderMessages();

  try {
    const r = await fetch(API_BASE + '/ai', {method:'POST', headers:authHeaders(), body:JSON.stringify(payload)});
    if (!r.ok) { const err = await r.json().catch(()=>({})); throw new Error(err.detail?.message || err.detail || 'Request failed'); }
    const data = await r.json();
    const msgs = chatHistories[activeAssistant.id];
    msgs[msgs.length - 1] = {role:'assistant', results:data.results, metadata:data.metadata, errors:data.errors};
    renderMessages();
  } catch(e) {
    const msgs = chatHistories[activeAssistant.id];
    msgs[msgs.length - 1] = {role:'assistant', error: e.message};
    renderMessages();
    toast('Error: ' + e.message, 'error');
  }
}

async function sendStream(payload) {
  const streamMsg = {role:'assistant', streamContent:''};
  chatHistories[activeAssistant.id].push(streamMsg);
  renderMessages();

  try {
    const r = await fetch(API_BASE + '/ai/stream', {method:'POST', headers:authHeaders(), body:JSON.stringify(payload)});
    if (!r.ok) { const err = await r.json().catch(()=>({})); throw new Error(err.detail?.message || err.detail || 'Stream failed'); }

    const reader = r.body.getReader();
    const decoder = new TextDecoder();
    let rawBuffer = '';
    let textContent = '';
    let completionData = null;

    while (true) {
      const {done, value} = await reader.read();
      if (done) break;
      rawBuffer += decoder.decode(value, {stream:true});

      const lines = rawBuffer.split('\\n');
      rawBuffer = lines.pop();

      for (const line of lines) {
        const trimmed = line.trim();
        if (!trimmed || !trimmed.startsWith('data:')) continue;
        const jsonStr = trimmed.slice(5).trim();
        if (!jsonStr) continue;
        try {
          const evt = JSON.parse(jsonStr);
          if (evt.type === 'token' && evt.data != null) {
            textContent += evt.data;
            const msgs = chatHistories[activeAssistant.id];
            msgs[msgs.length - 1].streamContent = textContent;
            updateLastMessage();
          } else if (evt.type === 'completion' && evt.results) {
            completionData = evt;
          }
        } catch(_) {}
      }
    }

    if (rawBuffer.trim()) {
      const trimmed = rawBuffer.trim();
      if (trimmed.startsWith('data:')) {
        try {
          const evt = JSON.parse(trimmed.slice(5).trim());
          if (evt.type === 'token' && evt.data != null) {
            textContent += evt.data;
          } else if (evt.type === 'completion' && evt.results) {
            completionData = evt;
          }
        } catch(_) {}
      }
    }

    const msgs = chatHistories[activeAssistant.id];
    if (completionData && completionData.results) {
      msgs[msgs.length - 1] = {
        role:'assistant',
        results: completionData.results,
        metadata: {
          total_batches: completionData.total_texts || 1,
          total_processing_time: completionData.total_processing_time
        },
        errors: completionData.errors || []
      };
    } else {
      msgs[msgs.length - 1].streamContent = textContent;
    }
    renderMessages();
  } catch(e) {
    const msgs = chatHistories[activeAssistant.id];
    msgs[msgs.length - 1] = {role:'assistant', error: e.message};
    renderMessages();
    toast('Stream error: ' + e.message, 'error');
  }
}

function esc(s) {
  if (!s) return '';
  const d = document.createElement('div');
  d.textContent = String(s);
  return d.innerHTML;
}

// Init
document.getElementById('tokenInput').addEventListener('input', () => { loadAssistants(); });

// Initialize app
(async function init() {
  await loadAuth0Config();
  handleAuthCallback();
  loadAssistants();
})();
</script>
</body>
</html>
"""
