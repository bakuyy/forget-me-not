import streamlit as st

st.title("🎙️ Voice Recognition with Google Web Speech API")

st.markdown(
    """
    <script>
        var speech_to_text = "";
        function startDictation() {
            if (window.hasOwnProperty('webkitSpeechRecognition')) {
                var recognition = new webkitSpeechRecognition();
                recognition.continuous = false;
                recognition.interimResults = false;
                recognition.lang = "en-US";
                recognition.start();
                
                recognition.onresult = function(e) {
                    speech_to_text = e.results[0][0].transcript;
                    document.getElementById('speechText').value = speech_to_text;
                    document.getElementById('speechForm').dispatchEvent(new Event('submit', { cancelable: true }));
                };
                
                recognition.onerror = function(e) {
                    console.log("Error:", e);
                };
            }
        }
    </script>
    <button onclick="startDictation()">🎤 Speak</button>
    <form id="speechForm" method="post">
        <input type="text" id="speechText" name="speechText" value="">
    </form>
    """,
    unsafe_allow_html=True
)

speech_text = st.text_input("Recognized Text:")

if speech_text:
    st.success(f"✅ You said: **{speech_text}**")

