(() => {
  const STORAGE_KEY = "ideasforgeai.language";
  const EVENT_NAME = "ideasforgeai:language-changed";
  const SUPPORTED = {
    en: { label: "English", nativeLabel: "English", dir: "ltr" },
    hi: { label: "Hindi", nativeLabel: "\u0939\u093f\u0928\u094d\u0926\u0940", dir: "ltr" },
    bn: { label: "Bengali", nativeLabel: "\u09ac\u09be\u0982\u09b2\u09be", dir: "ltr" }
  };
  const DICTIONARY = {
    en: {
      home_title: "You don't need to learn AI.",
      home_title_highlight: "You need to work with it.",
      home_subtitle:
        "Start with your problem. IdeasForgeAI helps you create your own tools, apps, code, documents, and workflows with AI - no AI expertise required.",
      home_placeholder: "Start writing your thought here...",
      chat_placeholder: "Message the AI",
      chip_studio: "ForgeStudio",
      chip_code: "ForgeCode",
      chip_work: "ForgeWork",
      sidebar_search: "Search chats",
      sidebar_library: "Library",
      sidebar_templates: "Templates",
      sidebar_knowledge: "Knowledge",
      sidebar_pinned: "Pinned",
      sidebar_projects: "Projects",
      sidebar_workspace: "Personal Workspace",
      menu_home: "Home",
      menu_new_chat: "New chat",
      menu_history: "Chat history",
      menu_language: "Language",
      menu_profile: "Profile",
      menu_projects: "Projects",
      profile_soon: "Profile settings will be connected next.",
      history_hint: "History is available inside ChatKit.",
      new_thread_hint: "Use ChatKit's new-thread control.",
      projects_hint: "Projects will be connected next.",
      onboarding_forgestudio_title: "Welcome to ForgeStudio",
      onboarding_forgestudio_intro:
        "Describe the app, website, design, document, image, or workflow you want to create, and IdeasForgeAI will help you shape it.",
      onboarding_forgecode_title: "Welcome to ForgeCode",
      onboarding_forgecode_intro:
        "Share the code problem, bug, feature, or repository task you want to work through, and we will guide the next safe step.",
      onboarding_forgework_title: "Welcome to ForgeWork",
      onboarding_forgework_intro:
        "Start with the business task, research need, report, or workflow you want to complete, and IdeasForgeAI will help structure it.",
      onboarding_idea_title: "Welcome to IdeasForgeAI",
      onboarding_idea_intro:
        "Start with your idea or problem, and IdeasForgeAI will help turn it into a clear next action.",
      onboarding_prompt_label: "Starting context",
      onboarding_hint: "Use the native composer below when you're ready.",
      onboarding_primary: "Start here",
      onboarding_secondary: "Hide",
      onboarding_suggestion_1: "Turn this into a practical plan.",
      onboarding_suggestion_2: "Show me the best first step.",
      onboarding_suggestion_3: "Help me refine the scope.",
      language_title: "Choose language",
      language_subtitle: "This changes the landing page and chat-page guidance.",
      language_saved: "Language updated."
    },
    hi: {
      home_title: "\u0906\u092a\u0915\u094b AI \u0938\u0940\u0916\u0928\u0947 \u0915\u0940 \u091c\u0930\u0942\u0930\u0924 \u0928\u0939\u0940\u0902 \u0939\u0948.",
      home_title_highlight: "\u0906\u092a\u0915\u094b \u0907\u0938\u0915\u0947 \u0938\u093e\u0925 \u0915\u093e\u092e \u0915\u0930\u0928\u093e \u0939\u0948.",
      home_subtitle:
        "\u0905\u092a\u0928\u0940 \u0938\u092e\u0938\u094d\u092f\u093e \u0938\u0947 \u0936\u0941\u0930\u0942 \u0915\u0930\u093f\u090f. IdeasForgeAI \u0906\u092a\u0915\u094b AI \u0915\u0940 \u091c\u094d\u091e\u093e\u0928 \u0915\u0947 \u092c\u093f\u0928\u093e \u0905\u092a\u0928\u0947 \u091f\u0942\u0932, \u090f\u092a, \u0915\u094b\u0921, \u0921\u0949\u0915\u094d\u092f\u0942\u092e\u0947\u0902\u091f \u0914\u0930 \u0935\u0930\u094d\u0915\u092b\u094d\u0932\u094b \u092c\u0928\u093e\u0928\u0947 \u092e\u0947\u0902 \u092e\u0926\u0926 \u0915\u0930\u0924\u093e \u0939\u0948.",
      home_placeholder: "\u0905\u092a\u0928\u093e \u0935\u093f\u091a\u093e\u0930 \u092f\u0939\u093e\u0901 \u0932\u093f\u0916\u0928\u093e \u0936\u0941\u0930\u0942 \u0915\u0930\u0947\u0902...",
      chat_placeholder: "AI \u0915\u094b \u0938\u0902\u0926\u0947\u0936 \u092d\u0947\u091c\u0947\u0902",
      chip_studio: "\u092b\u094b\u0930\u094d\u091c\u0938\u094d\u091f\u0942\u0921\u093f\u0913",
      chip_code: "\u092b\u094b\u0930\u094d\u091c\u0915\u094b\u0921",
      chip_work: "\u092b\u094b\u0930\u094d\u091c\u0935\u0930\u094d\u0915",
      sidebar_search: "\u091a\u0948\u091f \u0916\u094b\u091c\u0947\u0902",
      sidebar_library: "\u0932\u093e\u0907\u092c\u094d\u0930\u0947\u0930\u0940",
      sidebar_templates: "\u091f\u0947\u092e\u094d\u092a\u094d\u0932\u0947\u091f",
      sidebar_knowledge: "\u091c\u094d\u091e\u093e\u0928",
      sidebar_pinned: "\u092a\u093f\u0928 \u0915\u093f\u090f \u0917\u090f",
      sidebar_projects: "\u092a\u094d\u0930\u094b\u091c\u0947\u0915\u094d\u091f\u094d\u0938",
      sidebar_workspace: "\u092a\u0930\u094d\u0938\u0928\u0932 \u0935\u0930\u094d\u0915\u0938\u094d\u092a\u0947\u0938",
      menu_home: "\u0939\u094b\u092e",
      menu_new_chat: "\u0928\u092f\u093e \u091a\u0948\u091f",
      menu_history: "\u091a\u0948\u091f \u0939\u093f\u0938\u094d\u091f\u094d\u0930\u0940",
      menu_language: "\u092d\u093e\u0937\u093e",
      menu_profile: "\u092a\u094d\u0930\u094b\u092b\u093e\u0907\u0932",
      menu_projects: "\u092a\u094d\u0930\u094b\u091c\u0947\u0915\u094d\u091f\u094d\u0938",
      profile_soon: "\u092a\u094d\u0930\u094b\u092b\u093e\u0907\u0932 \u0938\u0947\u091f\u093f\u0902\u0917 \u091c\u0932\u094d\u0926 \u091c\u0941\u0921\u093c\u0947\u0917\u0940.",
      history_hint: "\u0939\u093f\u0938\u094d\u091f\u094d\u0930\u0940 ChatKit \u0915\u0947 \u0905\u0902\u0926\u0930 \u0909\u092a\u0932\u092c\u094d\u0927 \u0939\u0948.",
      new_thread_hint: "ChatKit \u0915\u093e new-thread control \u0907\u0938\u094d\u0924\u0947\u092e\u093e\u0932 \u0915\u0930\u0947\u0902.",
      projects_hint: "\u092a\u094d\u0930\u094b\u091c\u0947\u0915\u094d\u091f\u094d\u0938 \u091c\u0932\u094d\u0926 \u091c\u0941\u0921\u093c\u0947\u0902\u0917\u0947.",
      onboarding_forgestudio_title: "ForgeStudio \u092e\u0947\u0902 \u0938\u094d\u0935\u093e\u0917\u0924 \u0939\u0948",
      onboarding_forgestudio_intro:
        "\u0906\u092a \u091c\u094b \u090f\u092a, \u0935\u0947\u092c\u0938\u093e\u0907\u091f, \u0921\u093f\u091c\u093c\u093e\u0907\u0928, \u0921\u0949\u0915\u094d\u092f\u0942\u092e\u0947\u0902\u091f, \u0907\u092e\u0947\u091c \u092f\u093e \u0935\u0930\u094d\u0915\u092b\u094d\u0932\u094b \u092c\u0928\u093e\u0928\u093e \u091a\u093e\u0939\u0924\u0947 \u0939\u0948\u0902, \u0909\u0938\u0947 \u092c\u0924\u093e\u090f\u0901.",
      onboarding_forgecode_title: "ForgeCode \u092e\u0947\u0902 \u0938\u094d\u0935\u093e\u0917\u0924 \u0939\u0948",
      onboarding_forgecode_intro:
        "\u0915\u094b\u0921 \u0938\u092e\u0938\u094d\u092f\u093e, bug, feature \u092f\u093e repo task \u0938\u093e\u091d\u093e \u0915\u0930\u0947\u0902, \u0939\u092e \u0905\u0917\u0932\u093e \u0938\u0941\u0930\u0915\u094d\u0937\u093f\u0924 step \u0924\u092f \u0915\u0930\u0947\u0902\u0917\u0947.",
      onboarding_forgework_title: "ForgeWork \u092e\u0947\u0902 \u0938\u094d\u0935\u093e\u0917\u0924 \u0939\u0948",
      onboarding_forgework_intro:
        "\u092c\u093f\u091c\u0928\u0947\u0938 task, research, report \u092f\u093e workflow \u0938\u0947 \u0936\u0941\u0930\u0942 \u0915\u0930\u0947\u0902.",
      onboarding_idea_title: "IdeasForgeAI \u092e\u0947\u0902 \u0938\u094d\u0935\u093e\u0917\u0924 \u0939\u0948",
      onboarding_idea_intro:
        "\u0905\u092a\u0928\u0947 idea \u092f\u093e problem \u0938\u0947 \u0936\u0941\u0930\u0942 \u0915\u0930\u0947\u0902, \u0914\u0930 IdeasForgeAI \u0905\u0917\u0932\u093e step \u0938\u094d\u092a\u0937\u094d\u091f \u0915\u0930\u0947\u0917\u093e.",
      onboarding_prompt_label: "\u0936\u0941\u0930\u0942\u0906\u0924\u0940 context",
      onboarding_hint: "\u091c\u092c \u0906\u092a \u0924\u0948\u092f\u093e\u0930 \u0939\u094b\u0902, \u0928\u0940\u091a\u0947 native composer \u0915\u093e \u0909\u092a\u092f\u094b\u0917 \u0915\u0930\u0947\u0902.",
      onboarding_primary: "\u092f\u0939\u093e\u0901 \u0938\u0947 \u0936\u0941\u0930\u0942 \u0915\u0930\u0947\u0902",
      onboarding_secondary: "\u091b\u093f\u092a\u093e\u090f\u0901",
      onboarding_suggestion_1: "\u0907\u0938\u0947 \u090f\u0915 practical plan \u092e\u0947\u0902 \u092c\u0926\u0932\u094b.",
      onboarding_suggestion_2: "\u092e\u0941\u091d\u0947 \u0938\u092c\u0938\u0947 \u0905\u091a\u094d\u091b\u093e \u092a\u0939\u0932\u093e step \u0926\u093f\u0916\u093e\u090f\u0901.",
      onboarding_suggestion_3: "\u092e\u0947\u0930\u0940 scope refine \u0915\u0930\u0928\u0947 \u092e\u0947\u0902 \u092e\u0926\u0926 \u0915\u0930\u0947\u0902.",
      language_title: "\u092d\u093e\u0937\u093e \u091a\u0941\u0928\u0947\u0902",
      language_subtitle: "\u0907\u0938\u0938\u0947 landing page \u0914\u0930 chat guidance \u092c\u0926\u0932\u0947\u0917\u0940.",
      language_saved: "\u092d\u093e\u0937\u093e update \u0939\u094b \u0917\u0908."
    },
    bn: {
      home_title: "\u0986\u09aa\u09a8\u09be\u0995\u09c7 AI \u09b6\u09bf\u0996\u09a4\u09c7 \u09b9\u09ac\u09c7 \u09a8\u09be.",
      home_title_highlight: "\u0986\u09aa\u09a8\u09be\u0995\u09c7 \u098f\u09b0 \u09b8\u09be\u09a5\u09c7 \u0995\u09be\u099c \u0995\u09b0\u09a4\u09c7 \u09b9\u09ac\u09c7.",
      home_subtitle:
        "\u0986\u09aa\u09a8\u09be\u09b0 \u09b8\u09ae\u09b8\u09cd\u09af\u09be \u09a6\u09bf\u09df\u09c7 \u09b6\u09c1\u09b0\u09c1 \u0995\u09b0\u09c1\u09a8\u0964 IdeasForgeAI \u0986\u09aa\u09a8\u09be\u0995\u09c7 AI \u09a6\u0995\u09cd\u09b7\u09a4\u09be \u099b\u09be\u09dc\u09be \u09a8\u09bf\u099c\u09c7\u09b0 tool, app, code, document \u098f\u09ac\u0982 workflow \u09a4\u09c8\u09b0\u09bf \u0995\u09b0\u09a4\u09c7 \u09b8\u09be\u09b9\u09be\u09af\u09cd\u09af \u0995\u09b0\u09c7.",
      home_placeholder: "\u098f\u0996\u09be\u09a8\u09c7 \u0986\u09aa\u09a8\u09be\u09b0 \u099a\u09bf\u09a8\u09cd\u09a4\u09be \u09b2\u09c7\u0996\u09be \u09b6\u09c1\u09b0\u09c1 \u0995\u09b0\u09c1\u09a8...",
      chat_placeholder: "AI-\u0995\u09c7 \u09ac\u09be\u09b0\u09cd\u09a4\u09be \u09aa\u09be\u09a0\u09be\u09a8",
      chip_studio: "\u09ab\u09b0\u09cd\u099c\u09b8\u09cd\u099f\u09c1\u09a1\u09bf\u0993",
      chip_code: "\u09ab\u09b0\u09cd\u099c\u0995\u09cb\u09a1",
      chip_work: "\u09ab\u09b0\u09cd\u099c\u0993\u09df\u09be\u09b0\u09cd\u0995",
      sidebar_search: "\u099a\u09cd\u09af\u09be\u099f \u0996\u09c1\u0981\u099c\u09c1\u09a8",
      sidebar_library: "\u09b2\u09be\u0987\u09ac\u09cd\u09b0\u09c7\u09b0\u09bf",
      sidebar_templates: "\u099f\u09c7\u09ae\u09aa\u09cd\u09b2\u09c7\u099f",
      sidebar_knowledge: "\u099c\u09cd\u099e\u09be\u09a8",
      sidebar_pinned: "\u09aa\u09bf\u09a8 \u0995\u09b0\u09be",
      sidebar_projects: "\u09aa\u09cd\u09b0\u099c\u09c7\u0995\u09cd\u099f",
      sidebar_workspace: "\u09aa\u09be\u09b0\u09cd\u09b8\u09cb\u09a8\u09be\u09b2 \u0993\u09df\u09be\u09b0\u09cd\u0995\u09b8\u09cd\u09aa\u09c7\u09b8",
      menu_home: "\u09b9\u09cb\u09ae",
      menu_new_chat: "\u09a8\u09a4\u09c1\u09a8 \u099a\u09cd\u09af\u09be\u099f",
      menu_history: "\u099a\u09cd\u09af\u09be\u099f \u0987\u09a4\u09bf\u09b9\u09be\u09b8",
      menu_language: "\u09ad\u09be\u09b7\u09be",
      menu_profile: "\u09aa\u09cd\u09b0\u09cb\u09ab\u09be\u0987\u09b2",
      menu_projects: "\u09aa\u09cd\u09b0\u099c\u09c7\u0995\u09cd\u099f",
      profile_soon: "\u09aa\u09cd\u09b0\u09cb\u09ab\u09be\u0987\u09b2 settings \u09b6\u09bf\u0997\u0997\u09bf\u09b0\u0987 \u09af\u09c1\u0995\u09cd\u09a4 \u09b9\u09ac\u09c7.",
      history_hint: "History ChatKit-\u098f\u09b0 \u09ad\u09c7\u09a4\u09b0\u09c7 \u0985\u099b\u09c7.",
      new_thread_hint: "ChatKit-\u098f\u09b0 new-thread control \u09ac\u09cd\u09af\u09ac\u09b9\u09be\u09b0 \u0995\u09b0\u09c1\u09a8.",
      projects_hint: "Projects \u09b6\u09bf\u0997\u0997\u09bf\u09b0\u0987 \u09af\u09c1\u0995\u09cd\u09a4 \u09b9\u09ac\u09c7.",
      onboarding_forgestudio_title: "ForgeStudio-\u09a4\u09c7 \u09b8\u09cd\u09ac\u09be\u0997\u09a4",
      onboarding_forgestudio_intro:
        "\u0986\u09aa\u09a8\u09bf \u09af\u09c7 app, website, design, document, image \u09ac\u09be workflow \u09a4\u09c8\u09b0\u09bf \u0995\u09b0\u09a4\u09c7 \u099a\u09be\u09a8, \u09b8\u09c7\u099f\u09bf \u09a6\u09bf\u09df\u09c7 \u09b6\u09c1\u09b0\u09c1 \u0995\u09b0\u09c1\u09a8.",
      onboarding_forgecode_title: "ForgeCode-\u09a4\u09c7 \u09b8\u09cd\u09ac\u09be\u0997\u09a4",
      onboarding_forgecode_intro:
        "Code problem, bug, feature \u09ac\u09be repo task \u09a6\u09bf\u09df\u09c7 \u09b6\u09c1\u09b0\u09c1 \u0995\u09b0\u09c1\u09a8.",
      onboarding_forgework_title: "ForgeWork-\u09a4\u09c7 \u09b8\u09cd\u09ac\u09be\u0997\u09a4",
      onboarding_forgework_intro:
        "Business task, research, report \u09ac\u09be workflow \u09a6\u09bf\u09df\u09c7 \u09b6\u09c1\u09b0\u09c1 \u0995\u09b0\u09c1\u09a8.",
      onboarding_idea_title: "IdeasForgeAI-\u09a4\u09c7 \u09b8\u09cd\u09ac\u09be\u0997\u09a4",
      onboarding_idea_intro:
        "\u0986\u09aa\u09a8\u09be\u09b0 idea \u09ac\u09be problem \u09a6\u09bf\u09df\u09c7 \u09b6\u09c1\u09b0\u09c1 \u0995\u09b0\u09c1\u09a8, \u0986\u09b0 IdeasForgeAI \u09aa\u09b0\u09ac\u09b0\u09cd\u09a4\u09c0 step \u09b8\u09cd\u09aa\u09b7\u09cd\u099f \u0995\u09b0\u09ac\u09c7.",
      onboarding_prompt_label: "\u09b6\u09c1\u09b0\u09c1\u09b0 context",
      onboarding_hint: "\u0986\u09aa\u09a8\u09bf \u09aa\u09cd\u09b0\u09b8\u09cd\u09a4\u09c1\u09a4 \u09b9\u09b2\u09c7 \u09a8\u09bf\u099a\u09c7\u09b0 native composer \u09ac\u09cd\u09af\u09ac\u09b9\u09be\u09b0 \u0995\u09b0\u09c1\u09a8.",
      onboarding_primary: "\u098f\u0996\u09be\u09a8 \u09a5\u09c7\u0995\u09c7 \u09b6\u09c1\u09b0\u09c1 \u0995\u09b0\u09c1\u09a8",
      onboarding_secondary: "\u09b2\u09c1\u0995\u09be\u09a8",
      onboarding_suggestion_1: "\u098f\u099f\u09bf\u0995\u09c7 \u098f\u0995\u099f\u09bf practical plan-\u098f \u09aa\u09b0\u09bf\u09a3\u09a4 \u0995\u09b0\u09c1\u09a8.",
      onboarding_suggestion_2: "\u0986\u09ae\u09be\u0995\u09c7 \u09b8\u09c7\u09b0\u09be \u09aa\u09cd\u09b0\u09a5\u09ae step \u09a6\u09c7\u0996\u09be\u09a8.",
      onboarding_suggestion_3: "\u0986\u09ae\u09be\u09b0 scope refine \u0995\u09b0\u09a4\u09c7 \u09b8\u09be\u09b9\u09be\u09af\u09cd\u09af \u0995\u09b0\u09c1\u09a8.",
      language_title: "\u09ad\u09be\u09b7\u09be \u09ac\u09c7\u099b\u09c7 \u09a8\u09bf\u09a8",
      language_subtitle: "\u098f\u099f\u09bf landing page \u098f\u09ac\u0982 chat guidance \u09aa\u09b0\u09bf\u09ac\u09b0\u09cd\u09a4\u09a8 \u0995\u09b0\u09ac\u09c7.",
      language_saved: "\u09ad\u09be\u09b7\u09be update \u09b9\u09df\u09c7\u099b\u09c7."
    }
  };

  function normalizeLanguage(input) {
    const value = String(input || "").trim().toLowerCase();
    if (value.startsWith("hi")) return "hi";
    if (value.startsWith("bn") || value === "bengali") return "bn";
    return SUPPORTED[value] ? value : "en";
  }

  function readQueryLanguage() {
    try {
      return normalizeLanguage(new URLSearchParams(window.location.search).get("language"));
    } catch {
      return "en";
    }
  }

  function getCurrentLanguage() {
    try {
      const stored = localStorage.getItem(STORAGE_KEY);
      if (stored) return normalizeLanguage(stored);
    } catch {}
    return readQueryLanguage();
  }

  function applyDocumentLanguage(language) {
    const normalized = normalizeLanguage(language);
    document.documentElement.lang = normalized;
    document.documentElement.dir = SUPPORTED[normalized].dir || "ltr";
  }

  function translateKey(key) {
    const language = getCurrentLanguage();
    return (
      (DICTIONARY[language] && DICTIONARY[language][key]) ||
      (DICTIONARY.en && DICTIONARY.en[key]) ||
      key
    );
  }

  function setLanguage(language, options) {
    const normalized = normalizeLanguage(language);
    const settings = options || {};

    try {
      if (settings.persist !== false) {
        localStorage.setItem(STORAGE_KEY, normalized);
      }
    } catch {}

    applyDocumentLanguage(normalized);

    window.dispatchEvent(
      new CustomEvent(EVENT_NAME, {
        detail: {
          language: normalized,
          source: settings.source || "user"
        }
      })
    );

    return normalized;
  }

  function buildOnboardingMessages(entry, context) {
    const normalizedEntry = String(entry || "idea").trim().toLowerCase() || "idea";
    const prompt = String((context && context.prompt) || "").trim();
    const key = ["forgestudio", "forgecode", "forgework"].includes(normalizedEntry)
      ? normalizedEntry
      : "idea";
    return {
      title: translateKey("onboarding_" + key + "_title"),
      intro: translateKey("onboarding_" + key + "_intro"),
      promptLabel: translateKey("onboarding_prompt_label"),
      prompt,
      hint: translateKey("onboarding_hint"),
      primary: translateKey("onboarding_primary"),
      secondary: translateKey("onboarding_secondary"),
      suggestions: [
        translateKey("onboarding_suggestion_1"),
        translateKey("onboarding_suggestion_2"),
        translateKey("onboarding_suggestion_3")
      ]
    };
  }

  function ensureSelector() {
    let overlay = document.getElementById("if-language-overlay");
    if (overlay) return overlay;

    const style = document.createElement("style");
    style.id = "if-language-style";
    style.textContent = [
      ".if-language-overlay{position:fixed;inset:0;z-index:950;background:rgba(0,0,0,.56);display:none;align-items:flex-end;justify-content:center;padding:18px;backdrop-filter:blur(6px)}",
      ".if-language-overlay.open{display:flex}",
      ".if-language-panel{width:min(100%,420px);background:#101115;color:#fff;border:1px solid rgba(255,255,255,.12);border-radius:28px;padding:20px 18px 18px;box-shadow:0 24px 64px rgba(0,0,0,.36)}",
      ".if-language-head{display:flex;align-items:flex-start;justify-content:space-between;gap:12px;margin-bottom:14px}",
      ".if-language-head h2{margin:0;font-size:21px;line-height:1.1}",
      ".if-language-head p{margin:6px 0 0;color:rgba(255,255,255,.72);font-size:13px;line-height:1.5}",
      ".if-language-close{width:40px;height:40px;border-radius:14px;border:1px solid rgba(255,255,255,.14);background:rgba(255,255,255,.06);color:#fff;font-size:24px;cursor:pointer}",
      ".if-language-list{display:grid;gap:10px}",
      ".if-language-option{width:100%;padding:14px 16px;border-radius:18px;border:1px solid rgba(255,255,255,.12);background:#17191f;color:#fff;text-align:left;cursor:pointer}",
      ".if-language-option strong{display:block;font-size:15px}",
      ".if-language-option span{display:block;margin-top:4px;color:rgba(255,255,255,.68);font-size:13px}",
      ".if-language-option[data-active='true']{border-color:rgba(155,120,255,.8);box-shadow:0 0 0 1px rgba(155,120,255,.24) inset}",
      "@media (min-width: 769px){.if-language-overlay{align-items:center}.if-language-panel{border-radius:24px}}"
    ].join("");
    document.head.appendChild(style);

    overlay = document.createElement("div");
    overlay.id = "if-language-overlay";
    overlay.className = "if-language-overlay";
    overlay.innerHTML = [
      '<div class="if-language-panel" role="dialog" aria-modal="true" aria-labelledby="if-language-title">',
      '<div class="if-language-head">',
      "<div>",
      '<h2 id="if-language-title"></h2>',
      '<p id="if-language-subtitle"></p>',
      "</div>",
      '<button class="if-language-close" type="button" aria-label="Close">×</button>',
      "</div>",
      '<div class="if-language-list"></div>',
      "</div>"
    ].join("");
    document.body.appendChild(overlay);

    overlay.addEventListener("click", (event) => {
      if (event.target === overlay) {
        closeSelector();
      }
    });
    overlay.querySelector(".if-language-close").addEventListener("click", closeSelector);
    document.addEventListener("keydown", (event) => {
      if (event.key === "Escape") {
        closeSelector();
      }
    });

    return overlay;
  }

  function renderSelector() {
    const overlay = ensureSelector();
    overlay.querySelector("#if-language-title").textContent = translateKey("language_title");
    overlay.querySelector("#if-language-subtitle").textContent = translateKey("language_subtitle");

    const active = getCurrentLanguage();
    const list = overlay.querySelector(".if-language-list");
    list.innerHTML = "";

    Object.entries(SUPPORTED).forEach(([code, meta]) => {
      const button = document.createElement("button");
      button.type = "button";
      button.className = "if-language-option";
      button.setAttribute("data-active", String(code === active));
      button.innerHTML = "<strong>" + meta.nativeLabel + "</strong><span>" + meta.label + "</span>";
      button.addEventListener("click", () => {
        setLanguage(code, { persist: true, source: "selector" });
        closeSelector();
      });
      list.appendChild(button);
    });
  }

  function openSelector() {
    renderSelector();
    const overlay = ensureSelector();
    overlay.classList.add("open");
    document.body.classList.add("if-menu-open-lock");
  }

  function closeSelector() {
    const overlay = document.getElementById("if-language-overlay");
    if (!overlay) return;
    overlay.classList.remove("open");
    document.body.classList.remove("if-menu-open-lock");
  }

  function attachSwipeMenu(options) {
    const settings = options || {};
    const edge = typeof settings.edgeSize === "number" ? settings.edgeSize : 28;
    const closeDistance = typeof settings.closeDistance === "number" ? settings.closeDistance : 64;
    let tracking = null;

    document.addEventListener("pointerdown", (event) => {
      if (event.pointerType === "mouse" && event.buttons !== 1) return;
      tracking = {
        id: event.pointerId,
        startX: event.clientX,
        startY: event.clientY,
        active: !settings.isOpen() ? event.clientX <= edge : false,
        closing: !!settings.isOpen()
      };
    }, { passive: true });

    document.addEventListener("pointermove", (event) => {
      if (!tracking || tracking.id !== event.pointerId) return;
      const deltaX = event.clientX - tracking.startX;
      const deltaY = Math.abs(event.clientY - tracking.startY);
      if (deltaY > 32) {
        tracking = null;
        return;
      }
      if (tracking.active && deltaX > 56) {
        settings.open();
        tracking = null;
      } else if (tracking.closing && deltaX < -closeDistance) {
        settings.close();
        tracking = null;
      }
    }, { passive: true });

    document.addEventListener("pointerup", () => {
      tracking = null;
    }, { passive: true });

    document.addEventListener("pointercancel", () => {
      tracking = null;
    }, { passive: true });
  }

  applyDocumentLanguage(getCurrentLanguage());
  if (!document.getElementById("if-language-lock-style")) {
    const lockStyle = document.createElement("style");
    lockStyle.id = "if-language-lock-style";
    lockStyle.textContent = "body.if-menu-open-lock{overflow:hidden}";
    document.head.appendChild(lockStyle);
  }

  window.IdeasForgeLanguageAgent = {
    storageKey: STORAGE_KEY,
    supported: SUPPORTED,
    getCurrentLanguage,
    setLanguage,
    getLocale: getCurrentLanguage,
    getDirection() {
      return SUPPORTED[getCurrentLanguage()].dir || "ltr";
    },
    translateKey,
    openSelector,
    closeSelector,
    buildOnboardingMessages,
    attachSwipeMenu
  };
})();
