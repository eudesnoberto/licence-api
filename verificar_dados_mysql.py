#!/usr/bin/env python3
"""
Script para verificar dados migrados no MySQL
"""

import pymysql

# Configuração MySQL (HostGator)
MYSQL_HOST = "108.179.252.54"
MYSQL_PORT = 3306
MYSQL_DATABASE = "scpmtc84_api"
MYSQL_USER = "scpmtc84_api"
MYSQL_PASSWORD = "nQT-8gW%-qCY"

def main():
    print("=" * 60)
    print("📊 Verificando Dados no MySQL")
    print("=" * 60)
    print()
    
    try:
        conn = pymysql.connect(
            host=MYSQL_HOST,
            port=MYSQL_PORT,
            user=MYSQL_USER,
            password=MYSQL_PASSWORD,
            database=MYSQL_DATABASE,
            charset='utf8mb4',
            cursorclass=pymysql.cursors.DictCursor
        )
        
        cur = conn.cursor()
        
        # Verificar admin_users
        print("👤 Usuários Admin:")
        cur.execute("SELECT id, username, created_at FROM admin_users")
        admins = cur.fetchall()
        for admin in admins:
            print(f"   - ID: {admin['id']}, Usuário: {admin['username']}, Criado: {admin['created_at']}")
        print(f"   Total: {len(admins)}")
        print()
        
        # Verificar users
        print("👥 Usuários:")
        cur.execute("SELECT id, username, email, role, created_at FROM users")
        users = cur.fetchall()
        for user in users:
            print(f"   - ID: {user['id']}, Usuário: {user['username']}, Email: {user.get('email', 'N/A')}, Role: {user['role']}, Criado: {user['created_at']}")
        print(f"   Total: {len(users)}")
        print()
        
        # Verificar devices
        print("📱 Licenças (Devices):")
        cur.execute("SELECT id, device_id, owner_name, license_type, status, start_date, end_date, created_by FROM devices")
        devices = cur.fetchall()
        for device in devices:
            print(f"   - ID: {device['id']}, Device ID: {device['device_id'][:20]}..., Proprietário: {device.get('owner_name', 'N/A')}, Tipo: {device['license_type']}, Status: {device['status']}, Criado por: {device.get('created_by', 'N/A')}")
        print(f"   Total: {len(devices)}")
        print()
        
        # Verificar access_logs
        print("📝 Logs de Acesso:")
        cur.execute("SELECT COUNT(*) as total FROM access_logs")
        result = cur.fetchone()
        total_logs = result['total'] if result else 0
        print(f"   Total: {total_logs}")
        print()
        
        # Verificar blocked_devices
        print("🚫 Dispositivos Bloqueados:")
        cur.execute("SELECT COUNT(*) as total FROM blocked_devices")
        result = cur.fetchone()
        total_blocked = result['total'] if result else 0
        print(f"   Total: {total_blocked}")
        print()
        
        # Verificar license_history
        print("📜 Histórico de Licenças:")
        cur.execute("SELECT COUNT(*) as total FROM license_history")
        result = cur.fetchone()
        total_history = result['total'] if result else 0
        print(f"   Total: {total_history}")
        print()
        
        conn.close()
        
        print("=" * 60)
        print("✅ Verificação concluída!")
        print("=" * 60)
        
    except Exception as e:
        print(f"❌ Erro: {e}")

if __name__ == "__main__":
    main()

