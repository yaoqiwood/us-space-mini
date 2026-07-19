from app.db.session import get_session_local
from app.services.wechat_notifications import dispatch_pending_deliveries


def main() -> None:
    session = get_session_local()()
    try:
        delivered = dispatch_pending_deliveries(session)
    finally:
        session.close()
    print(f"Processed notification deliveries: {delivered}")


if __name__ == "__main__":
    main()
