from instagrapi import Client

def delete_sent_messages(username, password, target_username):
    cl = Client()
    try:
        cl.login(username, password)
    except Exception as e:
        print(f"❌ Login failed: {e}")
        return

    try:
        user_id = cl.user_id_from_username(target_username)
        threads = cl.direct_threads()
        found = False

        for thread in threads:
            if user_id in [u.pk for u in thread.users]:
                found = True
                print(f"📥 Found chat with {target_username}")
                for message in thread.messages:
                    if message.user_id == cl.user_id:
                        try:
                            cl.direct_delete_messages(thread_id=thread.id, message_ids=[message.id])
                            print(f"✅ Deleted message: {message.text}")
                        except Exception as e:
                            print(f"❌ Failed to delete message: {e}")
                break

        if not found:
            print("❌ Chat with user not found.")
    except Exception as e:
        print(f"❌ Error: {e}")


if __name__ == "__main__":
    print("📥 Instagram username:", end=" ")
    insta_user = input().strip()

    print("🔐 Instagram password:", end=" ")
    insta_pass = input().strip()

    print("👤 Target username (to delete messages sent to):", end=" ")
    target_user = input().strip()

    delete_sent_messages(insta_user, insta_pass, target_user) 
