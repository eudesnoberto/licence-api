import sqlite3
import config


DEVICE_ID = "d9f3d734d9ed4a078876d371a98ab211"


def main() -> None:
    conn = sqlite3.connect(config.DB_PATH)
    cur = conn.cursor()

    cur.execute(
        """
        INSERT OR IGNORE INTO devices (
          device_id, owner_name, license_type, status,
          start_date, end_date, custom_interval, features
        ) VALUES (
          ?, ?, ?, ?, ?, ?, ?, ?
        )
        """,
        (
            DEVICE_ID,
            "Cliente Teste",
            "anual",
            "active",
            "2025-01-01",
            "2026-01-01",
            60,
            "core",
        ),
    )

    conn.commit()
    conn.close()
    print("Licenca inserida/ja existente para:", DEVICE_ID)


if __name__ == "__main__":
    main()









