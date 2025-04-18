import docx
from docx.enum.section import WD_SECTION
from docx.shared import Pt
import string
import random
from io import BytesIO
import os
import time
import shutil



if __name__ == "__main__":
    pass
    path = "C:\\Users\\Stephan\\OneDrive\\Learning System\\Flashcards\\Probability and Statistics\\Hogg - Introduction to Mathematical Statistics - 8th\\Flashcards Word Files"
    filename = "08.01.docx"
    flashcards_empty = "flashcards empty.docx"
    #shutil.copy(os.path.join(path, filename), os.path.join(path, empty))
    doc = docx.Document(os.path.join(path, filename))
    doc_empty = docx.Document(os.path.join(path, filename))
    pass
    pass




    #
    # mat = [
    #     [1,2,0],
    #     [4,0,6],
    #     [0,8,9],
    #     [10],
    # ]
    # oldCount = 10
    # count = 0
    # MAX_COLS = 3
    # for i in reversed(range(len(mat))):
    #     if int(oldCount / ((i + 1) * MAX_COLS)) > 0:
    #         columns = MAX_COLS
    #     elif i > 0:
    #         columns = oldCount % (i * MAX_COLS)
    #     else:
    #         columns = oldCount
    #     for j in reversed(range(columns)):
    #         if mat[i][j] == 0:
    #             M = 0
    #             l = j + 1
    #             for k in range(i, len(mat)):
    #                     while l + 1 < MAX_COLS and M < count:
    #                         mat[k][l] = mat[k][l + 1]
    #                         l += 1
    #                         M += 1
    #                     l = 0
    #         count += 1
    #
    #
    # pass
    # pass
    # import matplotlib.pyplot as plt
    #
    # # Setting labels for items in Chart
    # Employee = ['Roshni', 'Shyam', 'Priyanshi',
    #             'Harshit', 'Anmol']
    #
    # # Setting size in Chart based on
    # # given values
    # Salary = [10000, 50000, 70000, 54000, 44000]
    #
    # # colors
    # colors = ['#FF0000', '#0000FF', '#FFFF00',
    #           '#ADFF2F', '#FFA500']
    #
    #
    # # Pie Chart
    # plt.pie(Salary, colors=colors, labels=Employee,
    #         autopct='%1.1f%%', pctdistance=0.85)
    #
    # # draw circle
    # centre_circle = plt.Circle((0, 0), 0.70, fc='white')
    # fig = plt.gcf()
    #
    # # Adding Circle in Pie chart
    # fig.gca().add_artist(centre_circle)
    #
    # # Adding Title of chart
    # plt.title('Employee Salary Details')
    #
    # # Displaying Chart
    # plt.show()
    # from yt_dlp import YoutubeDL
    # import subprocess
    #
    # videos = ['https://www.youtube.com/watch?v=y2Wp9E88QsQ','https://www.youtube.com/watch?v=shWhSEUX-5M']
    # # for video in videos:
    # #     subprocess.run(['yt-dlp', '-f', "bv+ba/b", video])
    # ydl_opts = {'format': 'mp4/bestvideo/best',}
    # with YoutubeDL(ydl_opts) as ydl:
    #     ydl.download(videos)
