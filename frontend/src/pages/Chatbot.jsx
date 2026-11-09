import { useEffect, useRef, useState } from "react";
import { Link } from "react-router-dom";
import { api } from "../lib/api";
import "../styles/Chatbot.css";

const MAX_MESSAGE_LENGTH = 500;

const CONTENT = {
  en: {
    backToDashboard: "← Back to Dashboard",
    introHeading: "Your AI Safety Companion",
    introText:
      "SAKHISAHAY's chatbot provides verified guidance on situations such as being followed, reporting harassment, travelling alone, and handling emergencies.",
    emergencyNotice:
      "If you are in immediate danger in India, call 112. Do not wait for a chatbot response.",
    languageLabel: "Language",
    chatTitle: "SAKHISAHAY Safety Assistant",
    botName: "SAKHISAHAY AI",
    youName: "You",
    welcome:
      "Hello! I am your SAKHISAHAY safety companion. You can ask me safety questions or select one of the suggested topics below. In an emergency, always call 112 directly.",
    suggestedHeading: "Suggested questions",
    inputPlaceholder: "Type your safety question here...",
    inputLabel: "Type your message",
    send: "Send",
    typing: "SAKHISAHAY AI is typing...",
    errorEmpty: "Please type a message before sending.",
    errorTooLong: `Your message is too long. Please keep it under ${MAX_MESSAGE_LENGTH} characters.`,
    charCount: "characters",
  },
  kn: {
    backToDashboard: "← ಡ್ಯಾಶ್‌ಬೋರ್ಡ್‌ಗೆ ಹಿಂತಿರುಗಿ",
    introHeading: "ನಿಮ್ಮ AI ಸುರಕ್ಷತಾ ಸಂಗಾತಿ",
    introText:
      "ಯಾರಾದರೂ ಹಿಂಬಾಲಿಸುವುದು, ಕಿರುಕುಳದ ದೂರು ನೀಡುವುದು, ಒಂಟಿಯಾಗಿ ಪ್ರಯಾಣಿಸುವುದು ಮತ್ತು ತುರ್ತು ಪರಿಸ್ಥಿತಿಗಳಂತಹ ಸಂದರ್ಭಗಳಲ್ಲಿ ಪರಿಶೀಲಿಸಿದ ಮಾರ್ಗದರ್ಶನ ನೀಡಲು SAKHISAHAY ಚಾಟ್‌ಬಾಟ್ ವಿನ್ಯಾಸಗೊಳಿಸಲಾಗಿದೆ.",
    emergencyNotice:
      "ಭಾರತದಲ್ಲಿ ನೀವು ತಕ್ಷಣದ ಅಪಾಯದಲ್ಲಿದ್ದರೆ 112 ಗೆ ಕರೆ ಮಾಡಿ. ಚಾಟ್‌ಬಾಟ್ ಉತ್ತರಕ್ಕಾಗಿ ಕಾಯಬೇಡಿ.",
    languageLabel: "ಭಾಷೆ",
    chatTitle: "SAKHISAHAY ಸುರಕ್ಷತಾ ಸಹಾಯಕ",
    botName: "SAKHISAHAY AI",
    youName: "ನೀವು",
    welcome:
      "ನಮಸ್ಕಾರ! ನಾನು ನಿಮ್ಮ SAKHISAHAY ಸುರಕ್ಷತಾ ಸಂಗಾತಿ. ನೀವು ಯಾವುದೇ ಸುರಕ್ಷತಾ ಪ್ರಶ್ನೆಗಳನ್ನು ಕೇಳಬಹುದು ಅಥವಾ ಕೆಳಗಿನ ಸಲಹೆಗಳನ್ನು ಆಯ್ಕೆ ಮಾಡಬಹುದು. ತಕ್ಷಣದ ತುರ್ತು ಪರಿಸ್ಥಿತಿಯಲ್ಲಿ 112 ಗೆ ಕರೆ ಮಾಡಿ.",
    suggestedHeading: "ಸೂಚಿತ ಪ್ರಶ್ನೆಗಳು",
    inputPlaceholder: "ನಿಮ್ಮ ಸುರಕ್ಷತಾ ಪ್ರಶ್ನೆಯನ್ನು ಇಲ್ಲಿ ಟೈಪ್ ಮಾಡಿ...",
    inputLabel: "ನಿಮ್ಮ ಸಂದೇಶವನ್ನು ಟೈಪ್ ಮಾಡಿ",
    send: "ಕಳುಹಿಸಿ",
    typing: "SAKHISAHAY AI ಟೈಪ್ ಮಾಡುತ್ತಿದೆ...",
    errorEmpty: "ಕಳುಹಿಸುವ ಮೊದಲು ದಯವಿಟ್ಟು ಸಂದೇಶವನ್ನು ಟೈಪ್ ಮಾಡಿ.",
    errorTooLong: `ನಿಮ್ಮ ಸಂದೇಶ ತುಂಬಾ ಉದ್ದವಾಗಿದೆ. ದಯವಿಟ್ಟು ${MAX_MESSAGE_LENGTH} ಅಕ್ಷರಗಳ ಒಳಗೆ ಇರಿಸಿ.`,
    charCount: "ಅಕ್ಷರಗಳು",
  },
};

const DEFAULT_SUGGESTED_QUESTIONS = {
  en: [
    { key: "followed", text: "What should I do if someone follows me?" },
    { key: "harassment", text: "How can I report harassment?" },
    { key: "travel", text: "How can I stay safe while travelling alone?" },
    { key: "emergency", text: "What should I do in an emergency?" },
  ],
  kn: [
    { key: "followed", text: "ಯಾರಾದರೂ ನನ್ನನ್ನು ಹಿಂಬಾಲಿಸಿದರೆ ನಾನು ಏನು ಮಾಡಬೇಕು?" },
    { key: "harassment", text: "ಕಿರುಕುಳದ ಬಗ್ಗೆ ನಾನು ಹೇಗೆ ದೂರು ನೀಡಬಹುದು?" },
    { key: "travel", text: "ಒಂಟಿಯಾಗಿ ಪ್ರಯಾಣಿಸುವಾಗ ನಾನು ಹೇಗೆ ಸುರಕ್ಷಿತವಾಗಿರಬಹುದು?" },
    { key: "emergency", text: "ತುರ್ತು ಪರಿಸ್ಥಿತಿಯಲ್ಲಿ ನಾನು ಏನು ಮಾಡಬೇಕು?" },
  ],
};

function Chatbot() {
  const [language, setLanguage] = useState("en");
  const [messages, setMessages] = useState([
    {
      id: "welcome-msg",
      sender: "bot",
      text: CONTENT.en.welcome,
      timestamp: new Date().toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" }),
    },
  ]);
  const [inputText, setInputText] = useState("");
  const [isTyping, setIsTyping] = useState(false);
  const [validationError, setValidationError] = useState("");
  const [suggestedQuestions, setSuggestedQuestions] = useState(DEFAULT_SUGGESTED_QUESTIONS.en);

  const messagesEndRef = useRef(null);
  const inputRef = useRef(null);
  const t = CONTENT[language];

  // Load FAQ from backend on language change
  useEffect(() => {
    async function fetchFaqs() {
      try {
        const faqs = await api.get(`/chatbot/faq?language=${language}`);
        if (Array.isArray(faqs) && faqs.length > 0) {
          setSuggestedQuestions(
            faqs.map((f, i) => ({ key: `faq-${i}`, text: f.question }))
          );
        } else {
          setSuggestedQuestions(DEFAULT_SUGGESTED_QUESTIONS[language]);
        }
      } catch {
        setSuggestedQuestions(DEFAULT_SUGGESTED_QUESTIONS[language]);
      }
    }

    fetchFaqs();
  }, [language]);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages, isTyping]);

  const handleLanguageChange = (newLang) => {
    setLanguage(newLang);
    setMessages((prev) => [
      ...prev,
      {
        id: `lang-switch-${Date.now()}`,
        sender: "bot",
        text: CONTENT[newLang].welcome,
        timestamp: new Date().toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" }),
      },
    ]);
  };

  const sendMessage = async (textToSend) => {
    const cleanText = textToSend.trim();
    if (!cleanText) {
      setValidationError(t.errorEmpty);
      return;
    }
    if (cleanText.length > MAX_MESSAGE_LENGTH) {
      setValidationError(t.errorTooLong);
      return;
    }

    setValidationError("");
    const userTimestamp = new Date().toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" });

    const userMessage = {
      id: `user-${Date.now()}`,
      sender: "user",
      text: cleanText,
      timestamp: userTimestamp,
    };

    setMessages((prev) => [...prev, userMessage]);
    setInputText("");
    setIsTyping(true);

    try {
      const response = await api.post("/chatbot/message", {
        message: cleanText,
        language,
      });

      const botMessage = {
        id: `bot-${Date.now()}`,
        sender: "bot",
        text: response.reply,
        resources: response.resources || [],
        disclaimer: response.disclaimer,
        timestamp: new Date().toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" }),
      };

      setMessages((prev) => [...prev, botMessage]);
    } catch {
      const errorMessage = {
        id: `bot-err-${Date.now()}`,
        sender: "bot",
        text:
          language === "kn"
            ? "ಕ್ಷಮಿಸಿ, ಸಂದೇಶವನ್ನು ಪ್ರಕ್ರಿಯೆಗೊಳಿಸಲು ಸಾಧ್ಯವಾಗಲಿಲ್ಲ. ತುರ್ತು ಪರಿಸ್ಥಿತಿಯಲ್ಲಿ 112 ಗೆ ಕರೆ ಮಾಡಿ."
            : "I'm sorry, I encountered an issue connecting to the safety service. If you are in immediate danger, please call 112.",
        timestamp: new Date().toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" }),
      };
      setMessages((prev) => [...prev, errorMessage]);
    } finally {
      setIsTyping(false);
      inputRef.current?.focus();
    }
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    sendMessage(inputText);
  };

  return (
    <div className="chatbot-page cb-page">
      <header className="chatbot-header cb-header">
        <div className="chatbot-header-inner cb-header-inner">
          <Link to="/dashboard" className="chatbot-back-link cb-back-link">
            {t.backToDashboard}
          </Link>
          <div className="chatbot-language cb-lang-switch">
            <span className="chatbot-language-label cb-lang-label">{t.languageLabel}:</span>
            <button
              type="button"
              className={`chatbot-lang-btn cb-lang-btn ${language === "en" ? "is-active" : ""}`}
              onClick={() => handleLanguageChange("en")}
            >
              English
            </button>
            <button
              type="button"
              className={`chatbot-lang-btn cb-lang-btn ${language === "kn" ? "is-active" : ""}`}
              onClick={() => handleLanguageChange("kn")}
            >
              ಕನ್ನಡ
            </button>
          </div>
        </div>
      </header>

      <main className="chatbot-main cb-main">
        {/* Real Emergency Notice Banner */}
        <div className="chatbot-emergency cb-emergency-banner" role="alert">
          <span className="cb-alert-icon" style={{ marginRight: "0.5rem" }}>⚠️</span>
          <span>
            {t.emergencyNotice}{" "}
            <a href="tel:112" style={{ fontWeight: 700, textDecoration: "underline", color: "#880E4F" }}>
              Call 112
            </a>
          </span>
        </div>

        <section className="chatbot-card cb-chat-card">
          <div className="chatbot-card-header cb-chat-header">
            <h2 className="chatbot-card-title">{t.chatTitle}</h2>
            <span className="chatbot-card-tag cb-status-badge">● Online</span>
          </div>

          <div className="chatbot-messages cb-messages-area" role="log" aria-live="polite">
            {messages.map((msg) => (
              <div
                key={msg.id}
                className={`chatbot-row cb-msg-row ${msg.sender === "user" ? "chatbot-row-user cb-user-row" : "chatbot-row-bot cb-bot-row"}`}
              >
                <div className={`chatbot-bubble cb-bubble ${msg.sender === "user" ? "chatbot-bubble-user cb-user-bubble" : "chatbot-bubble-bot cb-bot-bubble"}`}>
                  <span className="chatbot-sender cb-bubble-sender">
                    {msg.sender === "user" ? t.youName : t.botName}
                  </span>
                  <div className="chatbot-text cb-bubble-content" style={{ whiteSpace: "pre-wrap" }}>
                    {msg.text}
                  </div>
                  {msg.resources && msg.resources.length > 0 && (
                    <div style={{ marginTop: "0.6rem", borderTop: "1px solid rgba(0,0,0,0.08)", paddingTop: "0.4rem" }}>
                      <strong style={{ fontSize: "0.78rem", color: "#880E4F", display: "block", marginBottom: "0.25rem" }}>
                        Helplines:
                      </strong>
                      <div style={{ display: "flex", flexWrap: "wrap", gap: "0.4rem" }}>
                        {msg.resources.map((res) => (
                          <a
                            key={res.name}
                            href={`tel:${res.contact}`}
                            style={{
                              backgroundColor: "#FFE4E1",
                              color: "#880E4F",
                              padding: "0.2rem 0.5rem",
                              borderRadius: "4px",
                              fontSize: "0.8rem",
                              textDecoration: "none",
                              fontWeight: 600,
                            }}
                          >
                            📞 {res.name} ({res.contact})
                          </a>
                        ))}
                      </div>
                    </div>
                  )}
                  <span className="chatbot-time cb-bubble-time">{msg.timestamp}</span>
                </div>
              </div>
            ))}

            {isTyping && (
              <div className="chatbot-row chatbot-row-bot cb-msg-row cb-bot-row">
                <div className="chatbot-bubble chatbot-bubble-bot chatbot-typing cb-bubble cb-bot-bubble">
                  <span className="chatbot-dot" />
                  <span className="chatbot-dot" />
                  <span className="chatbot-dot" />
                  <span style={{ marginLeft: "6px", fontSize: "0.85rem", color: "#6b6570" }}>{t.typing}</span>
                </div>
              </div>
            )}
            <div ref={messagesEndRef} />
          </div>

          {/* Suggested Quick Questions */}
          <div className="chatbot-suggestions cb-suggested">
            <h3 className="chatbot-suggestions-heading cb-suggested-label">{t.suggestedHeading}:</h3>
            <div className="chatbot-suggestions-list cb-suggested-chips">
              {suggestedQuestions.map((q) => (
                <button
                  key={q.key}
                  type="button"
                  className="chatbot-chip cb-chip"
                  onClick={() => sendMessage(q.text)}
                  disabled={isTyping}
                >
                  {q.text}
                </button>
              ))}
            </div>
          </div>

          {/* Input Form */}
          <form className="chatbot-form cb-input-form" onSubmit={handleSubmit}>
            <div className="chatbot-input-row cb-input-wrap">
              <input
                ref={inputRef}
                type="text"
                className="chatbot-input"
                value={inputText}
                onChange={(e) => {
                  setInputText(e.target.value);
                  setValidationError("");
                }}
                placeholder={t.inputPlaceholder}
                maxLength={MAX_MESSAGE_LENGTH}
                disabled={isTyping}
                aria-label={t.inputLabel}
              />
              <button
                type="submit"
                className="chatbot-send-btn cb-send-btn"
                disabled={isTyping || !inputText.trim()}
              >
                {t.send}
              </button>
            </div>
            <div className="chatbot-form-footer">
              {validationError ? (
                <span className="chatbot-error cb-val-error" role="alert">
                  {validationError}
                </span>
              ) : <span />}
              <span className={`chatbot-counter cb-char-counter ${inputText.length > MAX_MESSAGE_LENGTH ? "is-over" : ""}`}>
                {inputText.length}/{MAX_MESSAGE_LENGTH}
              </span>
            </div>
          </form>
        </section>
      </main>
    </div>
  );
}

export default Chatbot;
