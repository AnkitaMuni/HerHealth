import datetime
from db_connector import get_db_connection
from mysql.connector import Error

def calculate_predictions(user_id, new_cycle_id):
    """
    Calculates the next predicted cycle, ovulation, and creates a notification.
    This is called AFTER a new cycle has been saved.
    """
    conn = get_db_connection()
    if not conn:
        return False
    
    cursor = conn.cursor(dictionary=True)
    
    try:
        query = """
            SELECT start_date, length 
            FROM cycle 
            WHERE user_id = %s 
            ORDER BY start_date DESC 
            LIMIT 10
        """
        cursor.execute(query, (user_id,))
        cycles = cursor.fetchall()

        if not cycles or len(cycles) < 2:
            print(f"Not enough data for user {user_id} to predict.")
            return False

        cycle_lengths = []
        for i in range(len(cycles) - 1):
            diff = (cycles[i]['start_date'] - cycles[i+1]['start_date']).days
            if diff > 15 and diff < 45: 
                cycle_lengths.append(diff)
        
        if not cycle_lengths:
             avg_cycle_len = 28 
        else:
            avg_cycle_len = int(sum(cycle_lengths) / len(cycle_lengths))

        avg_period_len = int(sum(c['length'] for c in cycles) / len(cycles))
        
        last_start_date = cycles[0]['start_date']
        
        next_start_date = last_start_date + datetime.timedelta(days=avg_cycle_len)
        next_end_date = next_start_date + datetime.timedelta(days=avg_period_len)
        
        ovulation_date = next_start_date - datetime.timedelta(days=14)
        possible_end = next_start_date + datetime.timedelta(days=2)

        noti_query = """
            INSERT INTO notification (user_id, start_date, end_date, medication_stock, status)
            VALUES (%s, %s, %s, 'Check supplies for next cycle', 'pending')
        """
        cursor.execute(noti_query, (user_id, next_start_date, next_end_date))
        
        new_noti_id = cursor.lastrowid

        pred_query = """
            INSERT INTO prediction (
                cycle_id, 
                noti_id, 
                possible_start_end, 
                ovulation_date,
                
                -- These will be NULL, so the trigger will run --
                possible_start_start, 
                end, 
                length
            )
            VALUES (%s, %s, %s, %s, NULL, NULL, NULL)
        """
        cursor.execute(pred_query, (
            new_cycle_id, 
            new_noti_id, 
            possible_end,  
            ovulation_date 
        ))

        conn.commit()
        print(f"Successfully created prediction for user {user_id}. Trigger has run.")
        return True

    except Error as e:
        print(f"Error in prediction logic: {e}")
        conn.rollback()
        return False
    finally:
        cursor.close()
        conn.close()