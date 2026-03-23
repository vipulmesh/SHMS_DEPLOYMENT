import sqlite3
from datetime import datetime

DATABASE = 'database.db'

# ===========================
# DISPLAY MENU
# ===========================
def show_menu():
    print("\n" + "="*60)
    print("🏥 HEALTH MONITORING DATABASE MANAGER")
    print("="*60)
    print("1. View All Data")
    print("2. Add New Record")
    print("3. Update Record")
    print("4. Delete Record")
    print("5. Delete All Data")
    print("6. Search by Village")
    print("7. Database Statistics")
    print("8. Exit")
    print("="*60)

# ===========================
# VIEW ALL DATA
# ===========================
def view_all_data():
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM health_data ORDER BY id DESC')
    rows = cursor.fetchall()
    conn.close()
    
    if len(rows) == 0:
        print("\n❌ No data found in database.")
        return
    
    print("\n" + "="*100)
    print(f"{'ID':<5} {'Village':<20} {'Diarrhea':<10} {'Fever':<8} {'Rainfall':<10} {'Risk':<15} {'Date':<12}")
    print("="*100)
    
    for row in rows:
        print(f"{row[0]:<5} {row[1]:<20} {row[2]:<10} {row[3]:<8} {row[4]:<10} {row[5]:<15} {row[6]:<12}")
    
    print("="*100)
    print(f"Total Records: {len(rows)}\n")

# ===========================
# ADD NEW RECORD
# ===========================
def add_record():
    print("\n📝 ADD NEW RECORD")
    print("-"*60)
    
    village = input("Village Name: ").strip()
    diarrhea = int(input("Number of Diarrhea Cases: "))
    fever = int(input("Number of Fever Cases: "))
    print("Rainfall Level: 1) Low  2) Medium  3) High")
    rainfall_choice = input("Choose (1-3): ")
    
    rainfall_map = {'1': 'Low', '2': 'Medium', '3': 'High'}
    rainfall = rainfall_map.get(rainfall_choice, 'Low')
    
    # Calculate risk
    if diarrhea > 10 and rainfall == 'High':
        risk = 'High Risk'
    elif 5 <= diarrhea <= 10:
        risk = 'Medium Risk'
    else:
        risk = 'Safe'
    
    current_date = datetime.now().strftime('%Y-%m-%d')
    
    # Insert into database
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO health_data (village, diarrhea, fever, rainfall, risk, date)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', (village, diarrhea, fever, rainfall, risk, current_date))
    conn.commit()
    conn.close()
    
    print(f"\n✅ Record added successfully!")
    print(f"   Risk Level: {risk}")

# ===========================
# UPDATE RECORD
# ===========================
def update_record():
    view_all_data()
    
    try:
        record_id = int(input("\nEnter ID of record to update: "))
        
        conn = sqlite3.connect(DATABASE)
        cursor = conn.cursor()
        
        # Check if record exists
        cursor.execute('SELECT * FROM health_data WHERE id = ?', (record_id,))
        record = cursor.fetchone()
        
        if not record:
            print(f"\n❌ No record found with ID {record_id}")
            conn.close()
            return
        
        print(f"\nCurrent Record:")
        print(f"Village: {record[1]}")
        print(f"Diarrhea Cases: {record[2]}")
        print(f"Fever Cases: {record[3]}")
        print(f"Rainfall: {record[4]}")
        print(f"Risk: {record[5]}")
        
        print("\n📝 Enter new values (press Enter to keep current value):")
        
        village = input(f"Village [{record[1]}]: ").strip() or record[1]
        diarrhea_input = input(f"Diarrhea Cases [{record[2]}]: ").strip()
        diarrhea = int(diarrhea_input) if diarrhea_input else record[2]
        fever_input = input(f"Fever Cases [{record[3]}]: ").strip()
        fever = int(fever_input) if fever_input else record[3]
        
        print(f"Rainfall (1=Low, 2=Medium, 3=High) [{record[4]}]: ", end='')
        rainfall_input = input().strip()
        rainfall_map = {'1': 'Low', '2': 'Medium', '3': 'High'}
        rainfall = rainfall_map.get(rainfall_input, record[4])
        
# Recalculate risk based on WHO-aligned thresholds
        if diarrhea > 10 and rainfall == 'High':
    # Exceeds outbreak threshold + environmental risk
         risk = 'High Risk'
        elif 5 <= diarrhea <= 10:
    # Alert threshold per WHO surveillance guidelines
         risk = 'Medium Risk'
        else:
    # Within normal expected range
         risk = 'Safe'

        
        # Update database
        cursor.execute('''
            UPDATE health_data 
            SET village = ?, diarrhea = ?, fever = ?, rainfall = ?, risk = ?
            WHERE id = ?
        ''', (village, diarrhea, fever, rainfall, risk, record_id))
        
        conn.commit()
        conn.close()
        
        print(f"\n✅ Record updated successfully!")
        print(f"   New Risk Level: {risk}")
        
    except ValueError:
        print("\n❌ Invalid input!")
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")

# ===========================
# DELETE RECORD
# ===========================
def delete_record():
    view_all_data()
    
    try:
        record_id = int(input("\nEnter ID of record to delete: "))
        
        confirm = input(f"⚠️  Are you sure you want to delete record {record_id}? (yes/no): ").lower()
        
        if confirm == 'yes':
            conn = sqlite3.connect(DATABASE)
            cursor = conn.cursor()
            cursor.execute('DELETE FROM health_data WHERE id = ?', (record_id,))
            
            if cursor.rowcount > 0:
                conn.commit()
                print(f"\n✅ Record {record_id} deleted successfully!")
            else:
                print(f"\n❌ No record found with ID {record_id}")
            
            conn.close()
        else:
            print("\n❌ Deletion cancelled.")
            
    except ValueError:
        print("\n❌ Invalid ID!")
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")

# ===========================
# DELETE ALL DATA
# ===========================
def delete_all_data():
    confirm = input("\n⚠️  WARNING: This will delete ALL records! Type 'DELETE ALL' to confirm: ")
    
    if confirm == 'DELETE ALL':
        conn = sqlite3.connect(DATABASE)
        cursor = conn.cursor()
        cursor.execute('DELETE FROM health_data')
        deleted_count = cursor.rowcount
        conn.commit()
        conn.close()
        
        print(f"\n✅ All data deleted! ({deleted_count} records removed)")
    else:
        print("\n❌ Deletion cancelled.")

# ===========================
# SEARCH BY VILLAGE
# ===========================
def search_by_village():
    village_name = input("\n🔍 Enter village name to search: ").strip()
    
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM health_data WHERE village LIKE ? ORDER BY id DESC', 
                   ('%' + village_name + '%',))
    rows = cursor.fetchall()
    conn.close()
    
    if len(rows) == 0:
        print(f"\n❌ No records found for village: {village_name}")
        return
    
    print("\n" + "="*100)
    print(f"{'ID':<5} {'Village':<20} {'Diarrhea':<10} {'Fever':<8} {'Rainfall':<10} {'Risk':<15} {'Date':<12}")
    print("="*100)
    
    for row in rows:
        print(f"{row[0]:<5} {row[1]:<20} {row[2]:<10} {row[3]:<8} {row[4]:<10} {row[5]:<15} {row[6]:<12}")
    
    print("="*100)
    print(f"Found {len(rows)} record(s)\n")

# ===========================
# DATABASE STATISTICS
# ===========================
def show_statistics():
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    
    # Total records
    cursor.execute('SELECT COUNT(*) FROM health_data')
    total = cursor.fetchone()[0]
    
    # Risk statistics
    cursor.execute('SELECT risk, COUNT(*) FROM health_data GROUP BY risk')
    risk_stats = cursor.fetchall()
    
    # Average cases
    cursor.execute('SELECT AVG(diarrhea), AVG(fever) FROM health_data')
    avg_data = cursor.fetchone()
    
    conn.close()
    
    print("\n" + "="*60)
    print("📊 DATABASE STATISTICS")
    print("="*60)
    print(f"Total Records: {total}")
    
    if total > 0:
        print(f"\nAverage Diarrhea Cases: {avg_data[0]:.2f}")
        print(f"Average Fever Cases: {avg_data[1]:.2f}")
        
        print("\nRisk Distribution:")
        for risk, count in risk_stats:
            percentage = (count / total) * 100
            print(f"  {risk}: {count} ({percentage:.1f}%)")
    
    print("="*60 + "\n")

# ===========================
# MAIN PROGRAM
# ===========================
def main():
    while True:
        show_menu()
        choice = input("Enter your choice (1-8): ").strip()
        
        if choice == '1':
            view_all_data()
        elif choice == '2':
            add_record()
        elif choice == '3':
            update_record()
        elif choice == '4':
            delete_record()
        elif choice == '5':
            delete_all_data()
        elif choice == '6':
            search_by_village()
        elif choice == '7':
            show_statistics()
        elif choice == '8':
            print("\n👋 Goodbye!\n")
            break
        else:
            print("\n❌ Invalid choice! Please enter 1-8.")
        
        input("\nPress Enter to continue...")

if __name__ == '__main__':
    main()