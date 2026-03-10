import os
import glob

def clean_project():
    print("🧹 Починаємо повне очищення...")

    # 1. Видаляємо базу даних
    if os.path.exists("db.sqlite3"):
        os.remove("db.sqlite3")
        print("✅ Базу даних (db.sqlite3) видалено.")
    else:
        print("ℹ️ Бази даних не знайдено (вже видалена).")

    # 2. Видаляємо файли міграцій (всі, що починаються з цифр)
    # Шукаємо в папці gear/migrations/
    migration_files = glob.glob(os.path.join("gear", "migrations", "[0-9]*.py"))
    
    if migration_files:
        for f in migration_files:
            try:
                os.remove(f)
                print(f"✅ Видалено міграцію: {f}")
            except Exception as e:
                print(f"❌ Не вдалося видалити {f}: {e}")
    else:
        print("ℹ️ Файлів міграцій не знайдено.")

    print("\n🎉 Очищення завершено! Тепер можна створювати нову базу.")

if __name__ == "__main__":
    clean_project()