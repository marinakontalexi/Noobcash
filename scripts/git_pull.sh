echo "Fetching from git to client1"
# sudo rm -r ntua-distributed-systems
# git clone https://github.com/marinakontalexi/Noobcash
git pull
echo "Succesfully fetched data"

echo "Copying to Client 2"
scp -rp /home/user/Documents/Noobcash client2:/home/user/Documents
echo "Copying to Client 3"
scp -rp /home/user/Documents/Noobcash client3:/home/user/Documents
echo "Copying to Client 4"
scp -rp /home/user/Documents/Noobcash client4:/home/user/Documents
echo "Copying to Client 5"
scp -rp /home/user/Documents/Noobcash client5:/home/user/Documents