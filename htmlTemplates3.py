css = '''
<style>
[data-testid="column"]{
    overflow: auto;
    height: 80vh;
    display: flex;
    flex-direction: column-reverse;
}

    
.block-container{
    padding-top: 2rem;
}
.chat-message {
    padding: 1.5rem; border-radius: 0.5rem; margin-bottom: 1rem; display: flex;
}
.chat-message.user {
    background-color: #8ECAE6
}
.chat-message.bot {
    background-color: #FCA311
}
.chat-message .avatar {
    width: 30%;
}
.chat-message .avatar img {
  max-width: 120px;
  max-height: 120px;
  border-radius: 50%;
  object-fit: cover;
}
.chat-message .message {
  width: 90%;
  padding: 0 1.5rem;
  color: #fffff;
}
.stTextInput {
  #position: fixed;
  #bottom: 3rem;
}
'''

bot_template = '''
<div class="chat-message bot">
    <div class="message">{{MSG}}</div>
</div>
'''

user_template = '''
<div class="chat-message user">
    <div class="message">{{MSG}}</div>
</div>
'''
