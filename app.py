import io
from flask import Flask, render_template, request, redirect, url_for, session, flash, send_file
from db_connector import get_db_connection, fetch_query
from prediction_logic import calculate_predictions
from mysql.connector import Error
import bcrypt
import datetime 
import json
from decimal import Decimal

app = Flask(__name__)
app.secret_key = 'your_very_secret_key' 

def json_serial(obj):
    """JSON serializer for objects not serializable by default json code"""
    if isinstance(obj, (datetime.date, datetime.datetime)):
        return obj.isoformat()
    if isinstance(obj, Decimal):
        return float(obj) 
    raise TypeError ("Type %s not serializable" % type(obj))

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        f_name = request.form['f_name']
        m_name = request.form.get('m_name') 
        l_name = request.form['l_name']
        email = request.form['email']
        phone = request.form['phone']
        dob = request.form['dob']
        password = request.form['password']
        country = request.form.get('country', 'India') 
        state = request.form['state']
        city = request.form['city']

        hashed_pw = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())

        conn = get_db_connection()
        if not conn:
            flash('Database connection failed.', 'danger')
            return render_template('register.html')
        
        cursor = conn.cursor()
        try:
            query = """INSERT INTO user (f_name, m_name, l_name, email, phone, dob, password, country, state, city) 
                           VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"""
            
            cursor.execute(query, (f_name, m_name, l_name, email, phone, dob, hashed_pw, country, state, city))
            conn.commit()
            flash('Registration successful! Please log in.', 'success')
            return redirect(url_for('login'))
        
        except Error as err:
            flash(f'Error: {err.msg}', 'danger') 
            conn.rollback() 
        finally:
            cursor.close()
            conn.close()

    return render_template('register.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        user = fetch_query("SELECT * FROM user WHERE email = %s", (email,))

        if user:
            user = user[0] 
            user_hashed_password = user['password'].encode('utf-8')
            
            if bcrypt.checkpw(password.encode('utf-8'), user_hashed_password):
                session['user_id'] = user['user_id']
                session['name'] = user['f_name']
                flash('Login successful!', 'success')
                return redirect(url_for('index'))
            else:
                flash('Invalid email or password', 'danger')
        else:
            flash('Invalid email or password', 'danger')

    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear() 
    flash('You have been logged out.', 'info')
    return redirect(url_for('login'))

@app.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        flash('Please log in to access the dashboard.', 'danger')
        return redirect(url_for('login'))

    user_id = session['user_id']
    
    noti_query = """
        SELECT * FROM notification
        WHERE user_id = %s AND status = 'pending'
        ORDER BY start_date ASC
    """
    pending_notifications = list(fetch_query(noti_query, (user_id,)))

    pred_query = """
        SELECT 
            p.*
        FROM prediction p
        JOIN cycle c ON p.cycle_id = c.cycle_id
        WHERE c.user_id = %s
        ORDER BY p.prediction_id DESC
        LIMIT 1
    """
    latest_prediction = fetch_query(pred_query, (user_id,))
    
    prediction_data = latest_prediction[0] if latest_prediction else None

    if prediction_data:
        try:
            predicted_start = prediction_data['possible_start_start']
            
            if isinstance(predicted_start, str):
                predicted_start_date = datetime.datetime.strptime(predicted_start, '%Y-%m-%d').date()
            else:
                predicted_start_date = predicted_start 
                
            today = datetime.date.today()
            days_until = (predicted_start_date - today).days
            
            dynamic_message = ""
            
            if 0 < days_until <= 10:
                dynamic_message = f"Your next cycle is predicted to start in {days_until} days."
            elif days_until == 0:
                dynamic_message = "Your next cycle is predicted to start today!"
            
            if dynamic_message:
                dynamic_notif = {
                    'noti_id': 0,
                    'user_id': user_id,
                    'start_date': today,
                    'end_date': None,
                    'medication_stock': dynamic_message, 
                    'status': 'pending'
                }
                pending_notifications.insert(0, dynamic_notif)
                
        except (KeyError, TypeError, ValueError) as e:
            print(f"Could not generate dynamic notification: {e}") 
            
    
    chart_query = """
        SELECT 
            start_date, 
            length, 
            weight, 
            height,
            DATEDIFF(start_date, LAG(start_date, 1) OVER (ORDER BY start_date)) AS full_cycle_length
        FROM cycle
        WHERE user_id = %s
        ORDER BY start_date ASC
    """
    
    all_cycles = fetch_query(chart_query, (user_id,))
    
    chart_data = {
        "labels": [c['start_date'].strftime('%b %d') for c in all_cycles],
        "weight": [c['weight'] for c in all_cycles],
        "height": [c['height'] for c in all_cycles],
        "period_length": [c['length'] for c in all_cycles],
        "cycle_length": [c['full_cycle_length'] for c in all_cycles]
    }
    
    chart_data_json = json.dumps(chart_data, default=json_serial)
    
    return render_template('dashboard.html', 
                           user_name=session['name'], 
                           notifications=pending_notifications, 
                           prediction=prediction_data,
                           chart_data=chart_data_json)

@app.route('/log_cycle', methods=['GET', 'POST'])
def log_cycle():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    user_id = session['user_id']

    if request.method == 'POST':
        start_date = request.form['start_date']
        end_date = request.form['end_date']
        mood = request.form['mood_swings']
        weight = request.form.get('weight') or None 
        height = request.form.get('height') or None 
        
        try:
            s_date = datetime.datetime.strptime(start_date, '%Y-%m-%d')
            e_date = datetime.datetime.strptime(end_date, '%Y-%m-%d')
            length = (e_date - s_date).days + 1 
            
            if length <= 0:
                flash('End date must be after start date.', 'danger')
                return render_template('log_cycle.html')

        except ValueError:
            flash('Invalid date format.', 'danger')
            return render_template('log_cycle.html')

        conn = get_db_connection()
        cursor = conn.cursor()
        
        try:
            query = """
                INSERT INTO cycle (user_id, start_date, end_date, length, mood_swings, weight, height)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
            """
            cursor.execute(query, (user_id, start_date, end_date, length, mood, weight, height))
            
            new_cycle_id = cursor.lastrowid
            conn.commit()
            
            calculate_predictions(user_id, new_cycle_id)

            flash('New cycle logged and predictions updated!', 'success')
        
        except Error as e:
            conn.rollback()
            flash(f'Error logging cycle: {e.msg}', 'danger')
        finally:
            cursor.close()
            conn.close()
            
        return redirect(url_for('dashboard'))

    return render_template('log_cycle.html')

@app.route('/log_medicine', methods=['GET', 'POST'])
def log_medicine():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    user_id = session['user_id']
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True) 

    try:
        cursor.execute("""
            SELECT cycle_id 
            FROM cycle 
            WHERE user_id = %s 
            ORDER BY start_date DESC 
            LIMIT 1
        """, (user_id,))
        latest_cycle = cursor.fetchone()

        if not latest_cycle:
            flash('You must log a cycle before you can log medicine.', 'danger')
            return redirect(url_for('log_cycle'))
        
        current_cycle_id = latest_cycle['cycle_id']

        if request.method == 'POST':
            med_name = request.form['name_of_medicine']
            dosage = request.form.get('dosage')
            
            consultation_file = request.files.get('doctor_consultation')
            consultation_data = None 
            filename = None
            mimetype = None
            
            if consultation_file and consultation_file.filename != '':
                consultation_data = consultation_file.read()
                filename = consultation_file.filename
                mimetype = consultation_file.mimetype
                
                if len(consultation_data) > 16 * 1024 * 1024:
                    flash('File is too large (max 16MB).', 'danger')
                    return render_template('log_medicine.html')

            insert_query = """
                INSERT INTO medicine (cycle_id, name_of_medicine, dosage, 
                                      doctor_consultation, consultation_filename, consultation_mimetype)
                VALUES (%s, %s, %s, %s, %s, %s)
            """
            cursor.execute(insert_query, (current_cycle_id, med_name, dosage, 
                                          consultation_data, filename, mimetype))
            conn.commit()
            
            flash('Medicine logged successfully for your current cycle!', 'success')
            return redirect(url_for('history')) 

    except Error as e:
        conn.rollback()
        flash(f'Error logging medicine: {e.msg}', 'danger')
    finally:
        cursor.close()
        conn.close()

    return render_template('log_medicine.html')


@app.route('/history')
def history():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    user_id = session['user_id']
    
    cycles = fetch_query("""
        SELECT *
        FROM cycle 
        WHERE user_id = %s 
        ORDER BY start_date DESC
    """, (user_id,))
    
    medicines = fetch_query("""
        SELECT m.* FROM medicine m
        JOIN cycle c ON m.cycle_id = c.cycle_id
        WHERE c.user_id = %s
    """, (user_id,))

    converted_cycles = []
    if cycles:
        for cycle in cycles:
            try:
                cycle['start_date'] = datetime.datetime.strptime(cycle['start_date'], '%Y-%m-%d').date()
                cycle['end_date'] = datetime.datetime.strptime(cycle['end_date'], '%Y-%m-%d').date()
                converted_cycles.append(cycle)
            except (ValueError, TypeError):
                converted_cycles.append(cycle) 

    return render_template('history.html', cycles=converted_cycles, medicines=medicines)


@app.route('/consultation/<int:med_id>')
def get_consultation(med_id):
    if 'user_id' not in session:
        return redirect(url_for('login'))

    user_id = session['user_id']

    file_query = """
        SELECT m.doctor_consultation, m.consultation_filename, m.consultation_mimetype
        FROM medicine m
        JOIN cycle c ON m.cycle_id = c.cycle_id
        WHERE m.med_id = %s AND c.user_id = %s
    """
    
    result = fetch_query(file_query, (med_id, user_id))

    if result and result[0] and result[0]['doctor_consultation']:
        blob_data = result[0]['doctor_consultation']
        filename = result[0]['consultation_filename']
        mimetype = result[0]['consultation_mimetype']

        if filename and mimetype:
            return send_file(
                io.BytesIO(blob_data),
                mimetype=mimetype,
                as_attachment=True,
                download_name=filename
            )
        else:
            return send_file(
                io.BytesIO(blob_data),
                mimetype='application/octet-stream', 
                as_attachment=True,
                download_name=f'consultation_{med_id}.dat' 
            )
            
    else:
        flash('No consultation file found or you do not have permission.', 'danger')
        return redirect(url_for('history'))

@app.route('/profile')
def profile():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    user_id = session['user_id']
    
    user_data = fetch_query("SELECT * FROM user WHERE user_id = %s", (user_id,))
    
    if not user_data:
        flash('User not found.', 'danger')
        return redirect(url_for('dashboard'))
        
    return render_template('profile.html', user=user_data[0])


@app.route('/dismiss_notification/<int:noti_id>')
def dismiss_notification(noti_id):
    if 'user_id' not in session:
        return redirect(url_for('login'))

    user_id = session['user_id']
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        query = """
            UPDATE notification 
            SET status = 'completed' 
            WHERE noti_id = %s AND user_id = %s
        """
        cursor.execute(query, (noti_id, user_id))
        conn.commit()
        
    except Error as e:
        conn.rollback()
        flash(f'Error dismissing notification: {e.msg}', 'danger')
    finally:
        cursor.close()
        conn.close()
        
    return redirect(url_for('dashboard'))


if __name__ == '__main__':
    app.run(debug=True)