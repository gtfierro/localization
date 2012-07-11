#Localization tools

##Web Tool So that I don't have to get my phone out to measure the wireless
signals, I created a web tool to help us out with everything. On the FitPC
(password '410soda'), in the ```localization``` directory, alter the
```flask_server.py``` and ```which.py``` files so that they have the MAC
address of the computer you're trying to monitor. Then, run ```python
flask_server.py <chan>```, where ```<chan>``` is the channel of the computer
you're trying to monitor. Remember, it has to be on airbears.

Now, walk to wherever you want to start sampling from with your laptop, and visit
the url ```http://128.32.44.132:8080/x,y/n```, where x,y are the coordinates of your position relative to the floor and n is the number of the sample you're taking.
The ip address is the ip of the FitPC

When you're done, visit ```http://128.32.44.132:8080/flush``` to save the
results to the file ```tmpdict.db``` on the FitPC.
