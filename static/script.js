// script.js

$(document).ready(function () {
    let currentAudio = null;

    // Helper: Stop current audio playback
    const stopCurrentAudio = () => {
        if (currentAudio && !currentAudio.paused) {
            currentAudio.pause();
            currentAudio.currentTime = 0;
            currentAudio = null;
        }
        $(".read-news-btn, .read-chat-btn, .read-input-chat-btn").css("background-color", "white");
    };

    // ======== NEWS: Fetch & Display ========
    $("#newsForm").submit(function (e) {
        e.preventDefault();
        const lang = $("#language").val();
        const topic = $("#topic").val();

        $.post("/get_news", { language: lang, topic: topic }, function (data) {
            const container = $("#newsContainer");
            container.empty();

            data.forEach(news => {
                const card = `
                    <div class="card mb-2">
                        <div class="card-header headline" style="cursor: pointer;">
                            ${news.title}
                            <button class="read-news-btn" 
                                    data-title="${news.title}" 
                                    data-description="${news.description}">
                                🔊
                            </button>
                        </div>
                        <div class="card-body description" style="display: none;">
                            <p>${news.description}</p>
                            <a href="${news.url}" target="_blank">Read full article</a>
                        </div>
                    </div>
                `;
                container.append(card);
            });

            // Toggle news description
            $(".headline").off("click").on("click", function () {
                $(this).next(".description").slideToggle();
            });

            // News TTS
            $(".read-news-btn").off("click").on("click", function () {
                const title = $(this).data("title");
                const description = $(this).data("description");
                const button = $(this);

                if (currentAudio && !currentAudio.paused) {
                    stopCurrentAudio();
                    return;
                }

                fetch("/read_news_loud", {
                    method: "POST",
                    headers: {
                        "Content-Type": "application/json"
                    },
                    body: JSON.stringify({ title, description })
                })
                .then(response => {
                    if (!response.ok) throw new Error("Failed to read news aloud");
                    return response.blob();
                })
                .then(blob => {
                    const audioUrl = URL.createObjectURL(blob);
                    currentAudio = new Audio(audioUrl);

                    stopCurrentAudio();
                    button.css("background-color", "#28a745");

                    currentAudio.play();
                    currentAudio.onended = () => {
                        currentAudio = null;
                        button.css("background-color", "white");
                    };
                })
                .catch(error => {
                    console.error("News voice playback error:", error);
                    button.css("background-color", "white");
                });
            });
        });
    });

    // ======== CHAT: Play chat messages aloud ========
    $(document).on("click", ".read-chat-btn", function () {
        const message = $(this).data("message");
        const button = $(this);

        if (!message) return;

        if (currentAudio && !currentAudio.paused) {
            stopCurrentAudio();
            return;
        }

        fetch("/read_message_loud", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({ title: "", description: message })
        })
        .then(response => {
            if (!response.ok) throw new Error("Failed to read message aloud");
            return response.blob();
        })
        .then(blob => {
            const audioUrl = URL.createObjectURL(blob);
            currentAudio = new Audio(audioUrl);

            stopCurrentAudio();
            button.css("background-color", "#28a745");

            currentAudio.play();
            currentAudio.onended = () => {
                currentAudio = null;
                button.css("background-color", "white");
            };
        })
        .catch(error => {
            console.error("Chat voice playback error:", error);
            button.css("background-color", "white");
        });
    });

    // ======== INPUT MIC: Voice to Text via Backend ========
    $("#mic-button").click(async function () {
        const selectedLang = $("#chat-language").val() || "en";

        if (!("webkitSpeechRecognition" in window)) {
            alert("Speech Recognition not supported in this browser.");
            return;
        }

        const recognition = new webkitSpeechRecognition();
        recognition.lang = selectedLang + "-IN"; 
        recognition.continuous = false;
        recognition.interimResults = false;

        $("#mic-button").css("background-color", "#ffc107");

        recognition.onresult = async function (event) {
            const transcript = event.results[0][0].transcript;

            const response = await fetch("/process_voice_input", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({
                    transcript: transcript,
                    language: selectedLang
                })
            });

            const result = await response.json();
            window.location.href = `/chat_voice_result?text=${encodeURIComponent(result.input_text)}`;
        };

        recognition.onerror = function () {
            $("#mic-button").css("background-color", "white");
        };

        recognition.onend = function () {
            $("#mic-button").css("background-color", "white");
        };

        recognition.start();
    });



    // ======== Sidebar Toggle ========
    $("#sidebarToggle").click(function () {
        $("#sidebar").toggleClass("visible");
    });

    // ======== Auto-scroll to bottom of chat ========
    const scrollChatToBottom = () => {
        const container = $("#chat-container");
        container.scrollTop(container.prop("scrollHeight"));
    };
    scrollChatToBottom();

    // ======== Optional UX: Enter key submits chat ========
    $("#chat-form input[type='text']").keypress(function (e) {
        if (e.which === 13 && !e.shiftKey) {
            e.preventDefault();
            $("#chat-form").submit();
        }
    });
});
