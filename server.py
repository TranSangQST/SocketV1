import socket
import time
import string

#Lưu ý: bind(): port must be 0-65535.

#Tạo 2 biến để giữ giá trị host và post
HOST = "127.0.0.1"
PORT = 3030
CHUNK_SIZE = 1024
CRLF = "\r\n"
LAST_CHUNK = hex(0)[2:]+ CRLF
#Khởi tạo server
def createServer(host,port):
	server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)


	server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
	server.bind((host,port))
	server.listen(4)
	return server

def createSocket():
	server=createServer(HOST,PORT)
	print("--Server has been created--")
	request=""
	while(request==""):
		client = getClientFromHttp(server)
		print("--Client has been recieved--\n")
		print("--Reading request--\n")
		request=getRequest(client)
		#time.sleep(10)
	return server,client,request


def getClientRequest():
	request=""
	while(request==""):
		client = getClientFromHttp(server)
		request=getRequest(client)
		print("Request has been recieved: ",request,"\n")
		#time.sleep(10)
	return client,request

#Get Client từ request từ trình duyệt
def getClientFromHttp(server):
	client,addrr=server.accept()
	print("client ",addrr," has connected to the server.")
	return client

#get request
def getRequest(client):
	dataStr=""
	client.settimeout(1)
	try:
		#data sẽ nhận yêu câu request từ client.recv(1024), 1024 tức là đọc 1024 kí tự
		#sau đó nhận cuỗi dataStr là dữ liệu sau khi data decode
		#Lặp đến khi nào chuỗi dataStr="", tức là đã hết request
		#Sau đó return dataStr trước khi nó ="", vẫn ko hiểu tại sao viết đc như thế :vvv
		data=client.recv(1024)
		dataStr=data.decode()
		while (true):
			data=client.recv(1024)
			dataStr = dataStr + data.decode()
			if(data.decode()==""):
				break;
	except socket.timeout: # fail after 1 second of no activity
		if not dataStr:
			print("Request timeout!!! \n")
	finally:
		# client.close()
		return dataStr

#response
def respondHomePage(server,client,request):
	while (1):
		statusCode="GET /index.html HTTP/1.1"
		if statusCode in request:
			fileName="index.html"
			respondPage(client,fileName)
			server.close()
			return

		statusCode="GET / HTTP/1.1"
		if statusCode in request:
			location="http://127.0.0.1:3030/index.html"
			goToPage(client,location)
			server.close()
			server,client,request=createSocket()
	
def respondRequestPage(server,client,request,fileName):
	statusCode="GET /%s HTTP/1.1"%fileName
	location="http://127.0.0.1:3030/%s"%fileName

	goToPage(client,location)
	server.close()
	server,client,request=createSocket()

	if statusCode in request:
		respondPage(client,fileName)
		server.close()

def goToPage(client,location):
	print("\n location ===== ",location,"\n\n")
	headerResponse ="""HTTP/1.1 301 Moved Permanently
Location: %s

"""%location
	client.send(bytes(headerResponse,'utf-8'))

def respondPage(client,fileName):
	print("\n filename ===== ",fileName,"\n\n")
	fi=open(fileName,"rb")
	content=fi.read()
	contentLength= len(content)
	print("contentLength=",contentLength)
	print("\n")
	headerResponse = """HTTP/1.1 200 OK
Content-Length: %d

"""%contentLength
	print("Header Response: \n ",headerResponse,"\n")
	response=headerResponse+content.decode()
	client.send(bytes(response,'utf-8'))

def respondRequestImg(server,client,request,imgName):
	statusCode="GET /%s HTTP/1.1"%imgName
	if statusCode in request:
		respondImg(client,imgName)

def respondImg(client, imgName):
	with open(imgName, 'rb') as fi:
		content=fi.read()
		contentLength= len(content)

		headerResponse ="""HTTP/1.1 200 OK
Content-Type: image/jpeg; charset=UTF-8
Content-Encoding: UTF-8
Content-Length: %d

"""%contentLength
		print("-----------------HTTP response: ")
		print(headerResponse)
		response=bytes(headerResponse,'utf-8')+content
		client.send(response)

def checkUserPass(request):
	if "POST / HTTP/1.1" not in request:
		return False
	if"Username=admin&Password=admin" in request:
		return True
	return False

def find_between( s, start, end ):
	return s[s.find(start)+len(start):s.rfind(end)]

# ########################
#def data_to_chunks(data, chunk_size):
#	total_size = len(data)
#	data_chunks = []
#	for i in range(0, total_size):
#		if (i%chunk_size) == 0:
#			chunk = data[i:(i+chunk_size)]
#			data_chunks.append(chunk)
#	return data_chunks

#def format_chunk(chunk):
#	format=("%X"%len(chunk)).encode() + CRLF.encode() + chunk + CRLF.encode()
#	return format

#def data_to_formatted_chunks(data, chunk_size):
#	return map(format_chunk, data_to_chunks(data, chunk_size))


#def sendFile(client,fileName):
#	with open(fileName, 'rb') as fi:
#		print("da mo duoc file %s\n"%fileName)

#		dataContent=fi.read()
#		statusCode = "HTTP/1.1 200 OK"+CRLF
#		contentType="Content-Type: text/plain" + CRLF
#		#contentType=""
#		endCodeIng = "Transfer-Encoding: chunked"+CRLF

#		headerResponse=statusCode+contentType+endCodeIng+CRLF
#		#headerResponse = headerResponse.encode()
#		client.send(bytes(headerResponse,'utf-8'))

#		#client.send(bytes(headerResponse,'utf-8'))
#		response=headerResponse
#		chunks=data_to_formatted_chunks(dataContent, CHUNK_SIZE)
#		for chunk in chunks:
#			#response += chunk
#			client.send(bytes(chunk,))
#		#response+=LAST_CHUNK.encode()
#		#print(response.decode(),"\n")
#		client.send(bytes(LAST_CHUNK,'utf-8'))
#		print(" da chunk xong")
#		#client.send(response)

def DataToChunks(data):
	length=len(data)
	chunks=[]
	for i in range (0,length):
		if (i%1024==0):
			chunk=data[i:(i+1024)]
			chunks.append(chunk)
	return chunks

def FormatChunk(chunk):
	Total=("%X" %len(chunk)).encode()+ CRLF.encode()+ chunk + CRLF.encode()
	return  Total
def convert(data):
	return map(FormatChunk,DataToChunks(data))
def SendFiles(Client,filename):
	f = open (filename, "rb")
	L = f.read()
	STATUS_LINE = "HTTP/1.1 200 OK" 
	ENCODING = "Transfer-Encoding: chunked"

	Client.send(bytes(
        STATUS_LINE + CRLF
       
        + ENCODING + CRLF
        + CRLF
        
        ,'utf-8'
        )
    )
	#Client.send(bytes(header,'utf-8'))
	chunks=convert(L)
	for chunk in chunks:
		Client.send(bytes(chunk,))

	Client.send(bytes(LAST_CHUNK,'utf-8'))
	Client.send(bytes(CRLF,'utf-8'))

if __name__ == "__main__":
	while (True):

		server,client,request=createSocket()
		respondHomePage(server,client,request)

		server,client,request=createSocket()
		print("Checking User and Password \n")
		print(request)
		checking=checkUserPass(request)

		if(checking):
			respondRequestPage(server,client,request,"info.html")
			listImg=["image1.jpg","image2.jpg"]
			server=createServer(HOST,PORT)

			for img in listImg:
				client,request=getClientRequest()
				print(request)
				print("\n")
				respondRequestImg(server,client,request,img)
			server.close()

			############################
			server,client,request=createSocket()
			print(request,"\n")
			fileName=find_between( request, "GET /", " HTTP/1.1" )
			print("filename:",fileName,":")
			print(request)
			respondRequestPage(server,client ,request,fileName)
			server.close()
			
			server=createServer(HOST,PORT)

			while True:					
				client,request=getClientRequest()
				fileName=find_between( request, "GET /", " HTTP/1.1" )
				SendFiles(client,fileName)
				
			server.shutdown(1)
			server.close()

		else:
			respondRequestPage(server,client,request,"404.html")



