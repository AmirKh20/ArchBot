#!/usr/bin/python3

import logging
from telegram import Update, KeyboardButton, ReplyKeyboardMarkup, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Updater,CallbackContext, CommandHandler, MessageHandler, Filters, CallbackQueryHandler
from flask import Flask, send_file
from os import listdir, system, makedirs, remove, chdir, path, getenv
from shutil import rmtree
from time import time
from hashlib import md5
from re import search
from glob import glob
from waitress import serve
from subprocess import check_output
from dotenv import load_dotenv
load_dotenv()

# Enable logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)

logger = logging.getLogger(__name__)
app = Flask(__name__)
app.debug = False
port = getenv("FLASK_PORT")
ip = check_output(['hostname', '-I']).strip().decode()

def reply(update, message):
    return update.message.reply_markdown_v2(message, reply_to_message_id = update.message.message_id)

def DefaultKeyboard(update, message):
    button = [
            [KeyboardButton("Make Archive 📦"), KeyboardButton("Make pdf 📄")],
            [KeyboardButton("List 🗄"), KeyboardButton("Remove Files 🗑")]
            ]
    if message is not None:
        update.message.reply_markdown_v2(message, reply_to_message_id = update.message.message_id,
                reply_markup=ReplyKeyboardMarkup(button, one_time_keyboard=False))
    else:
        update.message.reply_markdown_v2("Back to the main menu 🔙", reply_markup=ReplyKeyboardMarkup(button, one_time_keyboard=False))

def start(update, context):
    user = update.effective_user
    DefaultKeyboard(update, f"Hi {user.mention_markdown_v2()}\!")

def help_command(update, context):
    update.message.reply_text('Send /arch for making archive files after you sent your audios\n/ls for listing the files\n/rm for removing and re-sending the files')

def echo(update, context):
    update.message.reply_text(f"I don't know what you're taking about {update.effective_user['first_name']} 🤷")

def DownFiles(update, context):
    if update.message.document.file_size >= 20971520:
        return

    user = update.effective_user["id"]
    filename = update.message.document.file_name
    file = context.bot.getFile(update.message.document.file_id)

    if search("audio/.+",update.message.document.mime_type):
        directory = "MusicFiles"
    elif search("image/.+",update.message.document.mime_type):
        directory = "ImageFiles"
    else:
        directory = "Others"

    makedirs(f"{directory}/{user}", exist_ok=True)
    if path.exists(f"{directory}/{user}/{filename}"):
        reply(update, "File has alredy been downloaded\! See The list with /ls or send 'List 🗄'")
        return

    down_message = reply(update, "Downloading\.\.\.")
    file.download(f"./{directory}/{user}/{filename}")
    down_message.edit_text(f"Finished!\n{len(listdir(f'{directory}/{user}'))} Files Have been Downloaded")

def DownAudio(update, context):
    if update.message.audio.file_size >= 20971520:
        return

    audio = context.bot.getFile(update.message.audio.file_id)
    user = update.effective_user["id"]
    makedirs(f"MusicFiles/{user}", exist_ok=True)
    filename = update.message.audio.file_name

    if path.exists(f"MusicFiles/{user}/{filename}"):
        reply(update, "File has alredy been downloaded\! See The list with /ls or send 'List 🗄'")
        return

    down_message = reply(update, "Downloading\.\.\.")
    audio.download(f"./MusicFiles/{user}/{filename}")
    down_message.edit_text(f"Finished!\n{len(listdir(f'MusicFiles/{user}'))} Files Have been Downloaded")

def GetSortedName(user, directory, extension):
    files = glob(f"{directory}/{user}/*.{extension}")
    files.sort()
    fileNums = [int(x) for x in [i.split('/')[-1].split('.')[0] for i in files]]
    fileNums.sort()
    if not files:
        return f"0.{extension}"
    else:
        return f"{fileNums[-1] + 1}.{extension}"

def DownImages(update, context):
    if update.message.photo[-1].file_size >= 20971520:
        reply(update, "Size is too big\!")
        return

    image = context.bot.getFile(update.message.photo[-1].file_id)
    user = update.effective_user["id"]
    makedirs(f"ImageFiles/{user}", exist_ok=True)
    filename = GetSortedName(user, "ImageFiles", "jpg") + update.message.photo[-1].file_unique_id + ".jpg"
    #filename = GetSortedName(user, "ImageFiles", "jpg")

    #TODO: Hash checking ....
#    if path.exists(f"ImageFiles/{user}/{filename}"):
#        reply(update, "File has alredy been downloaded\! See The list with /ls or send 'List 🗄'")
#        return

    down_message = reply(update, "Downloading\.\.\.")
    image.download(f"./ImageFiles/{user}/{filename}")
    down_message.edit_text(f"Finished!\n{len(listdir(f'ImageFiles/{user}'))} Files Have Been Downloaded")
    #print(md5(open(f"./ImageFiles/{user}/{filename}", 'rb').read()).hexdigest())

def DownGif(update, context):
    if update.message.animation.file_size >= 20971520:
        return

    gif = context.bot.getFile(update.message.animation.file_id)
    user = update.effective_user["id"]
    makedirs(f"Others/{user}", exist_ok=True)
    filename = GetSortedName(user, "Others", "gif")

    #TODO: Hash checking ....
#    if path.exists(f"Others/{user}/{filename}"):
#        reply(update, "File has alredy been downloaded\! See The list with /ls or send 'List 🗄'")
#        return
    down_message = reply(update, "Downloading\.\.\.")
    gif.download(f"./Others/{user}/{filename}")
    down_message.edit_text(f"Finished!\n{len(glob(f'Others/{user}/*.gif'))} Files Have Been Downloaded")


def DownVideo(update, context):
    if update.message.video.file_size >= 20971520:
        return
    video = context.bot.getFile(update.message.video.file_id)
    user = update.effective_user["id"]
    makedirs(f"Others/{user}", exist_ok=True)
    filename = GetSortedName(user, "Others", "mp4") + update.message.video.file_unique_id + ".mp4"
    #filename = GetSortedName(user, "Others", "mp4")

    #TODO: Hash checking ....
#    if path.exists(f"Others/{user}/{filename}"):
#        reply(update, "File has alredy been downloaded\! See The list with /ls or send 'List 🗄'")
#        return
    down_message = reply(update, "Downloading\.\.\.")
    video.download(f"./Others/{user}/{filename}")
    down_message.edit_text(f"Finished!\n{len(glob(f'Others/{user}/*.mp4'))} Files Have Been Downloaded")


def GetSelectedList(directory):
    if directory == "MusicFiles":
        selectedList = "Musics 🎵"
    elif directory == "ImageFiles":
        selectedList = "Images 🖼"
    elif directory == "archiveFiles":
        selectedList = "Archive Files 📦"
    elif directory == "pdfs":
        selectedList = "PDFs 📄"
    elif directory == "Others":
        selectedList = "Others 🌀"
    return selectedList

def listFunc(directory, update):
    user = update.effective_user["id"]
    SelectedList = GetSelectedList(directory)

    if not path.exists(f"{directory}/{user}/") or listdir(f"{directory}/{user}") == []:
        update.message.reply_text(f"{SelectedList} is Empty!")
        return

    ListOfFiles = listdir(f"{directory}/{user}")
    ListOfFiles.sort()
    update.message.reply_text(SelectedList + ":\n" + '\n'.join(ListOfFiles))

def listFiles(update, context):
    user = update.effective_user["id"]
    if update.message.text == "List 🗄" or update.message.text == "/ls":
        button = [
                [KeyboardButton("List Musics 🎵"), KeyboardButton("List Images 🖼")],
                [KeyboardButton("List Archive Files 📦"), KeyboardButton("List PDFs 📄")],
                [KeyboardButton("List Others 🌀"), KeyboardButton("List All 🗄")],
                [KeyboardButton("Back To Main Menu 🔙")]
                ]
        update.message.reply_markdown_v2("Which one?", reply_to_message_id = update.message.message_id, reply_markup=ReplyKeyboardMarkup(button, one_time_keyboard=False))
        return

    elif update.message.text == "List Musics 🎵":
        listFunc("MusicFiles", update)

    elif update.message.text == "List Images 🖼":
        listFunc("ImageFiles", update)

    elif update.message.text == "List Archive Files 📦":
        listFunc("archiveFiles", update)

    elif update.message.text == "List PDFs 📄":
        listFunc("pdfs", update)

    elif update.message.text == "List Others 🌀":
        listFunc("Others", update)

    elif update.message.text == "List All 🗄":
        listFunc("MusicFiles", update)
        listFunc("ImageFiles", update)
        listFunc("archiveFiles", update)
        listFunc("pdfs", update)
        listFunc("Others", update)

    else:
        DefaultKeyboard(update, None)

def DelFunc(directory, update):
    user = update.effective_user["id"]
    SelectedList = GetSelectedList(directory)

    if not path.exists(f"{directory}/{user}") or listdir(f"{directory}/{user}") == []:
        update.message.reply_text(f"{SelectedList} is Empty!!")
        return

    rmtree(f"{directory}/{user}")
    reply(update, f"Deleted {SelectedList}")

def MakeInlineKeyboard(directory, user):
    ListOfFiles = listdir(f"{directory}/{user}")
    ListOfFiles.sort()
    keyboard = []
    for Index, Filename in enumerate(ListOfFiles):
        keyboard.append([InlineKeyboardButton(Filename, callback_data=str(Index))])
    keyboard.append([InlineKeyboardButton("All", callback_data=str(Index + 1))])
    return keyboard


def InlineDelete(directory, update):
    user = update.effective_user["id"]
    if not path.exists(f"{directory}/{user}") or listdir(f"{directory}/{user}") == []:
        update.message.reply_text(f"{GetSelectedList(directory)} is Empty!!")
        return

    keyboard = MakeInlineKeyboard(directory, user)
    update.message.reply_text(f'Which {directory} to Delete?', reply_markup=InlineKeyboardMarkup(keyboard))

def InlineDeleteAgain(directory, query, user):
    if listdir(f"{directory}/{user}") == []:
        query.edit_message_text(text=f"{GetSelectedList(directory)} is empty now")
        return

    keyboard = MakeInlineKeyboard(directory, user)
    query.edit_message_text(text=f'Which {directory} to Delete?', reply_markup=InlineKeyboardMarkup(keyboard))

def InlineButtons(update, context):
    query = update.callback_query
    query.answer()
    user = update.effective_user["id"]
    option = query.message.reply_markup.inline_keyboard[int(query.data)][0].text
    if option == "tar.gz":
        context.bot.send_message(chat_id = update.effective_chat.id, text = mktar(query, user))
        return
    if option == "zip":
        context.bot.send_message(chat_id = update.effective_chat.id, text = mkzip(query, user))
        return
    if option == "rar":
        context.bot.send_message(chat_id = update.effective_chat.id, text = mkrar(query, user))
        return

    directory = query.message.text.split()[1]
    if option == "All":
        SelectedList = GetSelectedList(directory)
        rmtree(f"{directory}/{user}")
        query.edit_message_text(text=f"Deleted {SelectedList}")
    else:
        remove(f"{directory}/{user}/{option}")
        InlineDeleteAgain(directory, query, user)

def delFiles(update, context):
    if update.message.text == "Remove Files 🗑" or update.message.text == "/rm":
        button = [
                [KeyboardButton("Delete Musics 🎵"), KeyboardButton("Delete Images 🖼")],
                [KeyboardButton("Delete Archive Files 📦"), KeyboardButton("Delete PDFs 📄")],
                [KeyboardButton("Delete Others 🌀"), KeyboardButton("Delete All 🗑")],
                [KeyboardButton("Back To Main Menu 🔙")]
                ]
        update.message.reply_markdown_v2("Which one?", reply_to_message_id = update.message.message_id,
                                                        reply_markup=ReplyKeyboardMarkup(button, one_time_keyboard=False))
        return

    if update.message.text == "Delete Musics 🎵":
        InlineDelete("MusicFiles", update)

    elif update.message.text == "Delete Images 🖼":
        InlineDelete("ImageFiles", update)

    elif update.message.text == "Delete Archive Files 📦":
        InlineDelete("archiveFiles", update)

    elif update.message.text == "Delete PDFs 📄":
        InlineDelete("pdfs", update)

    elif update.message.text == "Delete Others 🌀":
        InlineDelete("Others", update)

    elif update.message.text == "Delete All 🗑":
        DelFunc("MusicFiles", update)
        DelFunc("ImageFiles", update)
        DelFunc("archiveFiles", update)
        DelFunc("pdfs", update)
        DelFunc("Others", update)

def move(user):
    makedirs(f"MusicFiles/{user}", exist_ok=True)
    if glob(f"Others/{user}/*"):
        system(f"mv Others/{user}/* MusicFiles/{user}/")
    if glob(f"ImageFiles/{user}/*"):
        system(f"mv ImageFiles/{user}/* MusicFiles/{user}/")

def mktar(query, user):
    filepath = f'{user}/{md5( (str(time()) + str(user)).encode() ).hexdigest()}.tar.gz'
    arch_message = query.edit_message_text(text="Archiving...")
    move(user)
    system(f"tar czf archiveFiles/{filepath} -C MusicFiles/{user} . --remove-files")
    arch_message.edit_text("Finished!")
    return f"http://{ip}:{port}/Downloads/" + filepath

def mkzip(query, user):
    filepath = f'{user}/{md5( (str(time()) + str(user)).encode() ).hexdigest()}.zip'
    arch_message = query.edit_message_text(text="Archiving...")
    move(user)
    chdir(f"MusicFiles/{user}")
    system(f"zip -qq ../../archiveFiles/{filepath} *")
    chdir("../../")
    arch_message.edit_text("Finished!")
    rmtree(f"MusicFiles/{user}")
    return f"http://{ip}:{port}/Downloads/" + filepath

def mkrar(query, user):
    filepath = f'{user}/{md5( (str(time()) + str(user)).encode() ).hexdigest()}.rar'
    arch_message = query.edit_message_text(text="Archiving...")
    move(user)
    chdir(f"MusicFiles/{user}")
    system(f"rar a ../../archiveFiles/{filepath} * >>/dev/null")
    chdir("../../")
    arch_message.edit_text("Finished!")
    rmtree(f"MusicFiles/{user}")
    return f"http://{ip}:{port}/Downloads/" + filepath

def get_archive(update, context):
    user = update.effective_user["id"]
    if (not path.exists(f"MusicFiles/{user}") or listdir(f"MusicFiles/{user}") == []) and (not path.exists(f"ImageFiles/{user}") or listdir(f"ImageFiles/{user}") == []) and (not path.exists(f"Others/{user}") or listdir(f"Others/{user}") == []):
        reply(update, "ERROR\! You didnt give me any files\!")
        return

    keyboard = [
                [InlineKeyboardButton("tar.gz", callback_data='0')],
                [InlineKeyboardButton("zip", callback_data='1')],
                [InlineKeyboardButton("rar", callback_data='2')],
                ]
    update.message.reply_text(f'Which format to Archive and Compress?', reply_markup=InlineKeyboardMarkup(keyboard))
    makedirs(f"archiveFiles/{user}", exist_ok=True)

def get_pdf(update, context):
    user = update.effective_user["id"]
    if not path.exists(f"ImageFiles/{user}") or listdir(f"ImageFiles/{user}") == []:
        reply(update, "ERROR\! You didnt give me any files\!")
        return

    if update.message.text == "Make pdf 📄":
        button = [
                [KeyboardButton("Link 🌐"), KeyboardButton("File With Random Name 📁")],
                [KeyboardButton("Back To Main Menu 🔙")]
                ]
        update.message.reply_markdown_v2("Which one?, send a filename with '\.pdf' extension if you want to",
                reply_to_message_id = update.message.message_id, reply_markup=ReplyKeyboardMarkup(button, one_time_keyboard=True))
        return

    if update.message.text == "File With Random Name 📁" or update.message.text == "Link 🌐":
        filepath = f'{user}/{md5( (str(time()) + str(user)).encode() ).hexdigest()}.pdf'
    else:
        filepath = f'{user}/{update.message.text}'

    makedirs(f"pdfs/{user}", exist_ok=True)
    pdf_message = reply(update, "Creating the pdf\.\.\.")
    system(f"gm convert -size 595x842 ImageFiles/{user}/*.jpg -resize 595x842 -background white -compose Copy -gravity center -extent 595x842 pdfs/{filepath}")
    rmtree(f"ImageFiles/{user}")
    pdf_message.edit_text("Finished Creating!")

    if update.message.text == "Link 🌐":
        link = f"http://{ip}:{port}/Downloads/" + filepath
        context.bot.send_message(chat_id = update.effective_chat.id, text = link)
        DefaultKeyboard(update, None)
    else:
        up_message = reply(update, "Uploading\.\.\.")
        context.bot.send_document(chat_id = update.effective_chat.id, document = open(f"pdfs/{filepath}", 'rb'))
        up_message.edit_text("Finished Uploading!")
        remove(f"pdfs/{filepath}")
        DefaultKeyboard(update, None)

@app.route("/Downloads/<user>/<filename>")
def upfile(user, filename):
    if path.exists(f"archiveFiles/{user}/{filename}"):
        return send_file(f"archiveFiles/{user}/{filename}", as_attachment = True)

    if path.exists(f"pdfs/{user}/{filename}"):
        return send_file(f"pdfs/{user}/{filename}", as_attachment = True)

    return "404 File not Found"

def main() -> None:
    updater = Updater(getenv("BOT_TOKEN"))

    dispatcher = updater.dispatcher

    dispatcher.add_handler(CommandHandler("start", start))
    dispatcher.add_handler(CommandHandler("help", help_command))
    dispatcher.add_handler(CommandHandler("arch", get_archive))
    dispatcher.add_handler(CommandHandler("ls", listFiles))
    dispatcher.add_handler(CommandHandler("rm", delFiles))

    dispatcher.add_handler(MessageHandler(Filters.regex('^Make Archive 📦$'), get_archive))
    dispatcher.add_handler(MessageHandler(Filters.regex('^Make pdf 📄$') |
                                         Filters.regex("^Link 🌐$") | Filters.regex("^File With Random Name 📁$") | Filters.regex(".+\.pdf$"), get_pdf))

    dispatcher.add_handler(MessageHandler(Filters.regex('^List 🗄$') |
                                        Filters.regex('^List Musics 🎵$') | Filters.regex('^List Images 🖼$') |
                                        Filters.regex("^List Archive Files 📦$") | Filters.regex("^List PDFs 📄$") |
                                        Filters.regex("^List All 🗄$") | Filters.regex("^List Others 🌀$") |
                                        Filters.regex("^Back To Main Menu 🔙$"), listFiles))

    dispatcher.add_handler(MessageHandler(Filters.regex('^Remove Files 🗑$') |
                                         Filters.regex("^Delete Musics 🎵$") | Filters.regex("^Delete Images 🖼$") |
                                         Filters.regex("^Delete Archive Files 📦$") | Filters.regex("^Delete PDFs 📄$") |
                                         Filters.regex("^Delete Others 🌀$") | Filters.regex("^Delete All 🗑$"), delFiles))

    dispatcher.add_handler(CallbackQueryHandler(InlineButtons))
    dispatcher.add_handler(MessageHandler(Filters.audio, DownAudio))
    dispatcher.add_handler(MessageHandler(Filters.animation, DownGif))
    dispatcher.add_handler(MessageHandler(Filters.video, DownVideo))
    dispatcher.add_handler(MessageHandler(Filters.photo, DownImages))
    #TODO: Download Voices under 20 MB
    #TODO: Be able to download files with the same name but check them with md5
    dispatcher.add_handler(MessageHandler(Filters.document, DownFiles))
    dispatcher.add_handler(MessageHandler(Filters.text & ~Filters.command, echo))

    updater.start_polling()
    serve(app, host="0.0.0.0", port = int(port))

    updater.idle()

if __name__ == '__main__':
    main()
