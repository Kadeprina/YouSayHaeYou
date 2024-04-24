from firebase_admin import firestore, auth
import streamlit as st
from datetime import datetime

db = firestore.client()

# 사용자 입력 받기
user = None
try:
    user = auth.get_user_by_email(st.session_state["username"])
except auth.UserNotFoundError:
    st.error("사용자를 찾을 수 없습니다.")

uid = user.uid


def load_chat_message(uid):
    chat_history = []

    chats_ref = db.collection("chats").where("uid", "==", uid).order_by("timestamp",
                                                                        direction=firestore.Query.DESCENDING).stream()
    for chat in chats_ref:
        chat_data = chat.to_dict()
        chat_history.append(chat_data)
    return chat_history


def save_chat_message(message, uid):
    timestamp = datetime.now()
    chat_data = {
        "user": uid,
        "user_name": st.session_state["name"],
        "message": st.session_state["message"].payload,
        "actor": st.session_state["message"].actor,
        "timestamp": timestamp
    }
    db.collection("chats").add(chat_data)


# def imsi():
#     st.title("과거 채팅 기록 불러오기")
#
#     chat_history = load_chat_history()
#
#     # 과거 채팅 기록 출력
#     st.write("과거 채팅 기록:")
#     for chat in chat_history:
#         st.write(f"{chat['timestamp']} - {chat['user']}: {chat['message']}")


def delete_chat_message(uid):
    docs = db.collection("chats").where("uid", "==", uid).stream()
    for doc in docs:
        doc.reference.delete()


def save_button(email, uid):
    st.title("채팅 기록 저장 및 불러오기")

    message = st.text_area("메시지를 입력하세요:")

    # '전송' 버튼 클릭 시 채팅 저장
    if st.button("저장"):
        if uid.strip() != "" and message.strip() != "":
            save_chat_message(uid, message)
            st.success("채팅이 저장되었습니다!")
        else:
            st.error("사용자 UID 또는 메시지가 비어있습니다.")


def main(chat_input):
    with st.sidebar:
        c1, c2, c3 = st.columns(3)
        create_chat_button = c1.button(
            "채팅 내용 저장", use_container_width=True, key="create_chat_button"
        )
        if create_chat_button:
            try:
                save_chat_message(chat_input, uid)
                st.success("성공적으로 저장했습니다.")
            except Exception as e:
                st.error("저장 실패: ", e)

        load_chat_button = c2.button(
            "채팅 내용 불러오기", use_container_width=True, key="load_chat_button"
        )
        if load_chat_button:
            try:
                chat_history = load_chat_message(uid)
                st.session_state.messages = chat_history
                st.success("성공적으로 불러왔습니다.")
            except Exception as e:
                st.error("불러오기 실패: ", e)

        delete_chat_button = c3.button(
            "삭제", use_container_width=True, key="delete_chat_button"
        )
        if delete_chat_button:
            try:
                delete_chat_message(uid)
                st.success("성공적으로 삭제되었습니다.")
            except Exception as e:
                st.error("삭제 실패: ", e)
