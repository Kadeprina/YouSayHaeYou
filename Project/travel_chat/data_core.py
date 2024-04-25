from firebase_admin import firestore, auth
from google.cloud.firestore_v1 import aggregation
from google.cloud.firestore_v1.base_query import FieldFilter
import streamlit as st
import re
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

    chats_ref = db.collection("chats").where("user", "==", uid).get()
    sorted_docs = sorted(chats_ref, key=lambda doc: doc.id)

    for doc in sorted_docs:
        st.write(doc.id, doc.to_dict())

    # for chat in chats_ref:
    #     chat_data = chat.to_dict()
    #     chat_history.append(chat_data)
    # return chat_history


def save_chat_message(uid):
    timestamp = datetime.now()
    for i in range(len(st.session_state["messages"])):
        chat_data = {
            "user": uid,
            "user_name": st.session_state["name"],
            "message": st.session_state["messages"][i].payload,
            "actor": st.session_state["messages"][i].actor,
            "timestamp": timestamp
        }
        db.collection("chats").document(st.session_state["name"] + str(i)).set(chat_data)


# def imsi():
#     st.title("과거 채팅 기록 불러오기")
#
#     chat_history = load_chat_history()
#
#     # 과거 채팅 기록 출력
#     st.write("과거 채팅 기록:")
#     for chat in chat_history:
#         st.write(f"{chat['timestamp']} - {chat['user']}: {chat['message']}")


def delete_chat_message():
    collection_ref = db.collection("chats")
    query = collection_ref.where(filter=FieldFilter("user_name", "==", st.session_state["name"]))
    aggregate_query = aggregation.AggregationQuery(query)

    aggregate_query.count(alias="all")
    counts = aggregate_query.get()
    count = counts[0]
    count = re.search(r'value=(\d+)', str(count)).group(1)

    for i in range(int(count)):
        db.collection("chats").document(st.session_state["name"] + str(i)).delete()


# def save_button(email, uid):
#     st.title("채팅 기록 저장 및 불러오기")
#
#     message = st.text_area("메시지를 입력하세요:")
#
#     # '전송' 버튼 클릭 시 채팅 저장
#     if st.button("저장"):
#         if uid.strip() != "" and message.strip() != "":
#             save_chat_message(uid, message)
#             st.success("채팅이 저장되었습니다!")
#         else:
#             st.error("사용자 UID 또는 메시지가 비어있습니다.")


def main():
    with st.sidebar:
        c1, c2, c3 = st.columns(3)
        create_chat_button = c1.button(
            "채팅 내용 저장", use_container_width=True, key="create_chat_button"
        )
        if create_chat_button:
            try:
                save_chat_message(uid)
                st.success("성공적으로 저장했습니다.")
            except Exception as e:
                st.error("저장 실패: ", e)

        load_chat_button = c2.button(
            "채팅 내용 불러오기", use_container_width=True, key="load_chat_button"
        )
        if load_chat_button:
            try:
                chat_history = load_chat_message(uid)
                # st.session_state.messages = chat_history
                st.success("성공적으로 불러왔습니다.")
            except Exception as e:
                st.error("불러오기 실패: ", e)

        delete_chat_button = c3.button(
            "삭제", use_container_width=True, key="delete_chat_button"
        )
        if delete_chat_button:
            try:
                delete_chat_message()
                st.success("성공적으로 삭제되었습니다.")
            except Exception as e:
                st.error("삭제 실패: ", e)
