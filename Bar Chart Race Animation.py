import os
import warnings
import bar_chart_race as bcr
import pandas as pd
import tldextract
from moviepy.editor import VideoFileClip, AudioFileClip
import subprocess

def create_chart_from_excel(input_file, output_file="position_chart_race_with_audio", audio_file="your_audio.mp3"):
    # Suppress FutureWarning related to Series.fillna
    warnings.simplefilter(action='ignore', category=FutureWarning)
    # Suppress UserWarnings related to set_ticklabels
    warnings.simplefilter(action='ignore', category=UserWarning)
    # Read data from Excel file
    df = pd.read_excel(input_file)
    # Create a new column for extracted domain names
    df['Domain'] = df['Website'].apply(lambda x: f"{tldextract.extract(x).domain}.{tldextract.extract(x).suffix}")
    # Pivot the DataFrame for bar_chart_race
    df_pivot = df.pivot(index='Date', columns='Keyword', values='Amount')
    # Convert DataFrame values to numeric
    df_pivot = df_pivot.apply(pd.to_numeric, errors='coerce')
    # Create the bar chart race with a temporary filename
    temp_animation_path = "temp_animation.gif"
    bcr.bar_chart_race(
        df=df_pivot,
        filename=temp_animation_path,
        title=f'Applicants per Position on {df["Domain"].iloc[0]} ({min(df["Date"])} - {max(df["Date"])})',
        orientation='h',
        sort='desc',
        n_bars=5,
        period_length=500,
        fixed_order=False,
        steps_per_period=25,
        fixed_max=False,
        bar_texttemplate="{x:,.2f}",
        tick_template="{x:,.2f}",
        shared_fontdict=None,
        filter_column_colors=True,
        scale='linear',
        fig=None,
        writer='ffmpeg',  # Use Pillow for creating GIF
        period_summary_func=lambda v, r: {
            'x': .89,
            'y': .03,
            's': f'Made by @SerhiiVoinolovych',
            'ha': 'right',
            'size': 6
        }
    )
    # Convert the GIF to a temporary MP4 file
    temp_video_path = "temp_animation.mp4"
    ffmpeg_path = r'path to\ffmpeg-6.1.1-essentials_build\bin\ffmpeg.exe' #please download ffmpeg from website and use a path to it
    subprocess.run([ffmpeg_path, "-f", "gif", "-i", temp_animation_path, "-c:v", "libx264", "-pix_fmt", "yuv420p", temp_video_path], check=True)
    video_duration = VideoFileClip(temp_video_path).duration
    # Load audio clip
    audio_clip = AudioFileClip(audio_file)
    # Trim audio to match the minimum duration between video and audio
    min_duration = min(video_duration, audio_clip.duration)
    trimmed_audio_clip = audio_clip.subclip(0, min_duration)
    # Merge trimmed audio with the video
    final_output_file = f"{output_file}.mp4"
    final_clip = VideoFileClip(temp_video_path).set_audio(trimmed_audio_clip)
    final_clip.write_videofile(final_output_file, codec="libx264", audio_codec="aac", fps=24, threads=4)  
    # Use multiple threads for faster processing
    # Close the video and audio clips to release the files
    VideoFileClip(temp_video_path).close()
    audio_clip.close()
    # Clean up temporary animation and video files
# Clean up temporary animation and video files
    if os.path.exists(temp_animation_path):
        os.remove(temp_animation_path)

    if os.path.exists(temp_video_path):
        os.remove(temp_video_path)

    print(f"Chart with audio saved as {final_output_file}")

input_file = 'POSITIONS.xlsx'
input_file_name = input_file[:-5]
output_file = 'Chart_race_audio_' + input_file_name
audio_file = 'your_audio.mp3'
create_chart_from_excel(input_file, output_file, audio_file)
