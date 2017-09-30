from paramiko import SSHClient,AutoAddPolicy
from scp import SCPClient
import Image
from linebot.models import *

def get_reply(event) :
        os.system("touch test.jpg")
        message_content = line_bot_api.get_message_content(event.message.id)
        with open('test.jpg', 'wb') as fd:
            for chunk in message_content.iter_content():
                fd.write(chunk)
        img = Image.open('test.jpg')
        new_img= img.resize((240, 240),Image.ANTIALIAS)
        new_img.save('test-p.jpg',quality=100)
        server = "cscc.hsexpert.net"
        port = 22
        user = "apie0419"
        password = "a19970419"
        client = SSHClient()
        client.load_system_host_keys()
        client.set_missing_host_key_policy(AutoAddPolicy())
        client.connect(server, port, user, password)
        scp = SCPClient(client.get_transport())
        scp.put('test.jpg','public_html/test.jpg')
        scp.close()
        return ImageSendMessage(
                original_content_url="https://web-stu.tkucs.cc/404411240/test.jpg",
                preview_image_url="https://web-stu.tkucs.cc/404411240/test-p.jpg"
                )
        