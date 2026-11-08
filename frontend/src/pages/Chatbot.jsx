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
    } catch (err) {
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
    <div className="cb-page">
      <header className="cb-header">
        <div className="cb-header-inner">
          <Link to="/dashboard" className="cb-back-link">
            {t.backToDashboard}
          </Link>
          <div className="cb-lang-switch">
            <span className="cb-lang-label">{t.languageLabel}:</span>
            <button
              type="button"
              className={`cb-lang-btn ${language === "en" ? "is-active" : ""}`}
              onClick={() => handleLanguageChange("en")}
            >
              English
            </button>
            <button
              type="button"
              className={`cb-lang-btn ${language === "kn" ? "is-active" : ""}`}
              onClick={() => handleLanguageChange("kn")}
            >
              ಕನ್ನಡ
            </button>
          </div>
        </div>
      </header>

      <main className="cb-main">
        {/* Real Emergency Notice Banner */}
        <div className="cb-emergency-banner" role="alert">
          <span className="cb-alert-icon">⚠️</span>
          <p>
            {t.emergencyNotice}{" "}
            <a href="tel:112" style={{ fontWeight: 700, textDecoration: "underline", color: "#fff" }}>
              Call 112
            </a>
          </p>
        </div>

        <section className="cb-chat-card">
          <div className="cb-chat-header">
            <h2>{t.chatTitle}</h2>
            <span className="cb-status-badge">● Online</span>
          </div>

          <div className="cb-messages-area" role="log" aria-live="polite">
            {messages.map((msg) => (
              <div
                key={msg.id}
                className={`cb-msg-row ${msg.sender === "user" ? "cb-user-row" : "cb-bot-row"}`}
              >
                <div className={`cb-bubble ${msg.sender === "user" ? "cb-user-bubble" : "cb-bot-bubble"}`}>
                  <div className="cb-bubble-sender">
                    {msg.sender === "user" ? t.youName : t.botName}
                  </div>
                  <div className="cb-bubble-content" style={{ whiteSpace: "pre-wrap" }}>
                    {msg.text}
                  </div>
                  {msg.resources && msg.resources.length > 0 && (
                    <div style={{ marginTop: "0.75rem", borderTop: "1px solid rgba(0,0,0,0.08)", paddingTop: "0.5rem" }}>
                      <strong style={{ fontSize: "0.8rem", color: "#880E4F" }}>Helplines:</strong>
                      <div style={{ display: "flex", flexWrap: "wrap", gap: "0.4rem", marginTop: "0.3rem" }}>
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
                  <span className="cb-bubble-time">{msg.timestamp}</span>
                </div>
              </div>
            ))}

            {isTyping && (
              <div className="cb-msg-row cb-bot-row">
                <div className="cb-bubble cb-bot-bubble cb-typing-bubble">
                  <span>{t.typing}</span>
                </div>
              </div>
            )}
            <div ref={messagesEndRef} />
          </div>

          {/* Suggested Quick Questions */}
          <div className="cb-suggested">
            <span className="cb-suggested-label">{t.suggestedHeading}:</span>
            <div className="cb-suggested-chips">
              {suggestedQuestions.map((q) => (
                <button
                  key={q.key}
                  type="button"
                  className="cb-chip"
                  onClick={() => sendMessage(q.text)}
                  disabled={isTyping}
                >
                  {q.text}
                </button>
              ))}
            </div>
          </div>

          {/* Input Form */}
          <form className="cb-input-form" onSubmit={handleSubmit}>
            <div className="cb-input-wrap">
              <input
                ref={inputRef}
                type="text"
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
              <span className="cb-char-counter">
                {inputText.length}/{MAX_MESSAGE_LENGTH}
              </span>
            </div>
            <button
              type="submit"
              className="cb-send-btn"
              disabled={isTyping || !inputText.trim()}
            >
              {t.send}
            </button>
          </form>

          {validationError && (
            <p className="cb-val-error" role="alert">
              {validationError}
            </p>
          )}
        </section>
      </main>
    </div>
  );
}

export default Chatbot;
