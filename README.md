# Project Overview
## 1. WebSocket for Real-Time Communication
- Purpose: Stream audio from the client to the backend service.
- WebSocket Protocol: Allows for bidirectional communication between the client and server.
- Audio Streaming: Client sends raw audio data every 250 milliseconds.
- Transcription Frequency: Transcriptions are performed every second (4 chunks) to achieve near real-time speech-to-text conversion.
- Return transcribed text back to client in real time

## 2. Whisper Model 
- Purpose: Perform speech-to-text recognition.
- Model: Whisper model for efficient and accurate transcription.
- Model Size: Start with base/small first
- Deployment: Run locally on the host machine to avoid using OpenAI's API (quite expensive?)
- Other option: Hugging face's model

# 3. LLama3 Model
- Purpose: Perform error analysis on the transcriptions after the user has finished speaking.
- Output: Generate an error report and provide recommendations for improvement.
- Model Size: Start with 8B now, consider fine tune or upgrade to 70B later.
- Other option: Hugging face's model
- How to handle the poorly transcribed inputs gracefully

# 4. LangChain
- Purpose: Orchestrate the NLP tasks and manage the workflow.
- Functionality: Chain Whisper and LLama3: Create a pipeline that first processes the audio with Whisper and then analyzes the text with LLama3.
- Prompt Engineering: Craft prompts for LLama3 to ensure accurate and relevant error analysis.
- RAG (Retrieval-Augmented Generation): Future integration with a customized curriculum database for enhanced feedback and learning resources.

# 5. Verify JWT for Controlled Access
- Connection: Accept any WebSocket connection.
- JWT Token: Require the client to send their JWT token as the first message.
- Verification: Authenticate the token with the backend.
- Access Control: Allow further communication only if the JWT token is valid.

# 6.SSL Connection
- Encryption: Use SSL/TLS to secure the WebSocket connection.
- Certificates: Implement proper SSL certificates.
- Configuration: Configure the WebSocket server to use secure WebSockets (wss://).