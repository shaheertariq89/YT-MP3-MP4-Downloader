from flask import Flask, request, render_template,jsonify,send_file,send_from_directory
from pytube import YouTube
from flask_mail import Mail, Message
from pathlib import Path
import os
import re
Downloader = Flask(__name__)
# Flask-Mail configuration for Gmail
Downloader.config['MAIL_SERVER'] = 'smtp.gmail.com'
Downloader.config['MAIL_PORT'] = 587
Downloader.config['MAIL_USE_TLS'] = True
Downloader.config['MAIL_USERNAME'] = 'xyz@gmail.com'  # Your Gmail email address
Downloader.config['MAIL_PASSWORD'] = '*********'  # Your Gmail password
mail = Mail(Downloader)

@Downloader.route('/')
def home():
    return render_template('index.html')
# Define a route for a custom page
@Downloader.route('/custom')
def custom_page():
    return 'This is a custom page.'
progress = 0
def preprocess_title(title):
    # Remove '#' and extra spaces
    cleaned_title = re.sub(r'[\\/*?:"<>|#.\']', '', title)
    return cleaned_title
@Downloader.route("/download", methods=["GET", "POST"])
def download_video():
    message = ''
    error_type = 0
    if request.method == 'POST' and 'video_url1' in request.form:
        youtube_url = request.form["video_url1"]
        if youtube_url:
            validate_video_url = (
                r'(https?://)?(www\.)?'
                '(youtube|youtu|youtube-nocookie)\.(com|be)/'
                '(watch\?v=|embed/|v/|.+\?v=)?([^&=%\?]{11})')
            valid_video_url = re.match(validate_video_url, youtube_url)
            if valid_video_url:
                url = YouTube(youtube_url, on_progress_callback=progress_function)
                video = url.streams.get_highest_resolution()
                video_title = preprocess_title(url.title)
                print(video_title)
                # Define the default download folder
                video_filename = f'{video_title}'
                print(video_filename)
                default_download_folder = os.path.join(os.path.expanduser('~'), 'video-fetch')
                # Create the download folder if it doesn't exist
                os.makedirs(default_download_folder, exist_ok=True)
                video_path = os.path.join(default_download_folder, video_filename + '.mp4')
                # Download the video into the default download folder
                video.download(default_download_folder)
                # Rename the downloaded file to your desired filename




                message = 'Video Downloaded Successfully!'
                error_type = 1
                matching_files = [file for file in os.listdir(default_download_folder) if file.startswith(video_filename)]
                print('matcch',matching_files)
                if matching_files:
                    # If a matching file is found, send it to the user
                    matching_file = os.path.join(default_download_folder, matching_files[0])
                    match_exact =matching_files[0]
                    print('Exact: ',match_exact)
                    print(matching_file)
                    return send_from_directory(
                        default_download_folder,
                        match_exact,
                        as_attachment=True
                    )
                    print("send successfully")
                else:
                    print('File not found ')
            else:
                message = 'Enter Valid YouTube Video URL!'
                error_type = 0
        else:
            message = 'Enter YouTube Video Url.'
            error_type = 0
    return render_template('index.html', message=message, error_type=error_type)

@Downloader.route("/progress", methods=["GET"])
def progress():
    # Call the progress_function to get the progress
    progress_value = progress_function()
    # Return the progress value as JSON
    return jsonify(progress=progress_value)

def progress_function(stream=None, chunk=None, bytes_remaining=None):
    # Calculate the progress based on the parameters passed (if needed)
    # For simplicity, let's assume you have a global variable to store the progress
    global progress
    # If bytes_remaining is None, it means progress is requested through the /progress route
    if bytes_remaining is None:
        # Return the progress value directly
        return progress
    else:
        # Calculate progress based on bytes_remaining (or any other relevant parameters)
        total_size = float(stream.filesize)
        bytes_downloaded = float(total_size - bytes_remaining)
        percentage = (bytes_downloaded / total_size) * 100
        progress = percentage
        # Print progress for debugging
        print("progress is ", progress)
        # Return the progress value
        return progress





@Downloader.route("/download1", methods=["GET", "POST"])
def download_audio():
    message = ''
    error_type = 0
    print("Checking if audio is downloading or not")
    if request.method == 'POST' and 'video_url1' in request.form:
        youtube_url = request.form["video_url1"]

        if youtube_url:
            validate_video_url = (
                r'(https?://)?(www\.)?'
                '(youtube|youtu|youtube-nocookie)\.(com|be)/'
                '(watch\?v=|embed/|v/|.+\?v=)?([^&=%\?]{11})')
            valid_video_url = re.match(validate_video_url, youtube_url)

            if valid_video_url:
                try:
                    url = YouTube(youtube_url)
                    audio = url.streams.filter(only_audio=True).first()
                    audio_title = preprocess_title(url.title)
                    print(audio_title)
                    # Define the default download folder
                    audio_filename = f'{audio_title}'
                    print(audio_filename)
                    default_download_folder = os.path.join(os.path.expanduser('~'), 'audio-fetch')
                    # Create the download folder if it doesn't exist
                    os.makedirs(default_download_folder, exist_ok=True)
                    audio_path = os.path.join(default_download_folder, audio_filename + '.mp3')
                    # Download the audio into the default download folder
                    audio.download(output_path=default_download_folder, filename=audio_filename + '.mp3')

                    message = 'Audio Downloaded Successfully!'
                    error_type = 1
                    matching_files = [file for file in os.listdir(default_download_folder) if file.startswith(audio_filename)]
                    print('match', matching_files)
                    if matching_files:
                        # If a matching file is found, send it to the user
                        matching_file = os.path.join(default_download_folder, matching_files[0])
                        match_exact = matching_files[0]
                        print('Exact: ', match_exact)
                        print(matching_file)
                        return send_from_directory(
                            default_download_folder,
                            match_exact,
                            as_attachment=True
                        )
                        print("send successfully")
                    else:
                        print('File not found')
                except Exception as e:
                    message = f'Error: {e}'
                    error_type = 0
            else:
                message = 'Enter Valid YouTube Video URL!'
                error_type = 0
        else:
            message = 'Enter YouTube Video URL.'
            error_type = 0

    return render_template('index.html', message=message, error_type=error_type)

@Downloader.route('/terms-of-service')
def terms_of_service():
    return render_template('terms.html')
@Downloader.route('/about')
def about():
    return render_template('about.html')
@Downloader.route('/copyright')
def copyright():
    return render_template('copyright.html')


@Downloader.route('/feedback', methods=['GET', 'POST'])
def feedback():
    if request.method == 'GET':
        return render_template('feedback.html')
    if request.method == 'POST':
        user_email = request.form.get('userEmail')
        feedback_content = request.form.get('feedback')

        # Save the feedback in the backend
        save_feedback(user_email, feedback_content)

        # Send feedback to your email
        send_feedback_email(user_email, feedback_content)

        return jsonify({'message': 'Feedback submitted successfully!'})

def save_feedback(user_email, feedback_content):
    # Save the feedback in the backend (e.g., database)
    # Here you can implement code to save the feedback to your database
    pass

def send_feedback_email(user_email, feedback_content):
    # Send feedback via email
    msg = Message(subject='videofetchFeedback',
                  sender=user_email,  # Your Gmail email address
                  recipients=['xyz@gmail.com'])  # Your other email address where you want to forward the feedback
    msg.body = f"User Email: {user_email}\nFeedback: {feedback_content}"

    # Initialize Flask-Mail and send the email
    mail.send(msg)

    # You can also print the feedback to the console if needed
    print(f"User Email: {user_email}")
    print(f"Feedback: {feedback_content}")

if __name__ == '__main__':
    Downloader.run(host='0.0.0.0', port=5000, debug=True)
