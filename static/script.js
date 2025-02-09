$(document).ready(function () {
    let chatCount = 0;
    let chats = {};
    let selectedChatId = null;

    function saveChatHistory() {
        let chatContent = $("#messageFormeight").html().trim();

        if (chatContent === "" || (selectedChatId && chats[selectedChatId] === chatContent)) {
            return; // Prevent duplicate or empty chat history entries
        }

        let chatId = "chat_" + chatCount;
        chats[chatId] = chatContent;
        $("#chatHistory").append(`<li style="background: #202123; color: white; border-color: white; border-radius: 10px" class='list-group-item chat-item' data-id='${chatId}'>Chat ${chatCount + 1}</li>`);

        selectedChatId = chatId;
        chatCount++;
    }

    function loadChat(chatId) {
        if (chats[chatId]) {
            $("#messageFormeight").html(chats[chatId]);
            selectedChatId = chatId;
        }
    }

    $("#newChat").click(function () {
        saveChatHistory();

        $("#messageFormeight").html("");
        $("#text").val("");
        selectedChatId = null;
    });

    $("#clearAllChats").click(function () {
        chatCount = 0;
        chats = {};
        $("#chatHistory").html("");
        $("#messageFormeight").html("");
        selectedChatId = null;
    });

    $(document).on("click", ".chat-item", function () {
        let chatId = $(this).data("id");
        loadChat(chatId);
    });

    $("#uploadBtn").click(function () {
        var file = $("#pdfUpload")[0].files[0];
        if (file) {
            var formData = new FormData();
            formData.append("file", file);
            $.ajax({
                url: "/upload",
                type: "POST",
                data: formData,
                contentType: false,
                processData: false,
                success: function (response) {
                    alert("PDF uploaded successfully!");
                }
            });
        }
    });

    $("#messageArea").on("submit", function (event) {
        event.preventDefault();
        var rawText = $("#text").val().trim();

        if (rawText === "") return;

        var userHtml = `<div class="d-flex justify-content-end"><div class="msg_cotainer_send">${rawText}</div></div>`;
        $("#text").val("");
        $("#messageFormeight").append(userHtml);

        $.ajax({
            data: { msg: rawText },
            type: "POST",
            url: "/get",
        }).done(function (data) {
            var botHtml = `<div class="d-flex justify-content-start"><div class="msg_cotainer">${data}</div></div>`;
            $("#messageFormeight").append(botHtml);
        });
    });

    $("#clearChat").click(function () {
        $("#messageFormeight").html("");
        $("#text").val("");
    });
});