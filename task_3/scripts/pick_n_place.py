#!/usr/bin/env python3


'''
This is a boiler plate script that contains hint about different services that are to be used
to complete the task.
Use this code snippet in your code or you can also continue adding your code in the same file


This python file runs a ROS-node of name offboard_control which controls the drone in offboard mode. 
See the documentation for offboard mode in px4 here() to understand more about offboard mode 
This node publishes and subsribes the following topics:

     Services to be called                   Publications                                          Subscriptions				
    /mavros/cmd/arming                       /mavros/setpoint_position/local                       /mavros/state
    /mavros/set_mode                         /mavros/setpoint_velocity/cmd_vel                     /mavros/local_position/pose   
         
    
'''

import rospy
from geometry_msgs.msg import *
from mavros_msgs.msg import *
from mavros_msgs.srv import *
from gazebo_ros_link_attacher.srv import *
from rospy.impl.transport import BIDIRECTIONAL

class offboard_control:
    def __init__(self):
        # Initialise rosnode
        rospy.init_node('offboard_control', anonymous=True)
        
    def setArm(self, value=True):
        # Calling to /mavros/cmd/arming to arm the drone and print fail message on failure
        rospy.wait_for_service('mavros/cmd/arming')  # Waiting untill the service starts 
        try:
            armService = rospy.ServiceProxy('mavros/cmd/arming', mavros_msgs.srv.CommandBool) # Creating a proxy service for the rosservice named /mavros/cmd/arming for arming the drone 
            result=armService(value)
            print(result)
        except rospy.ServiceException as e:
            print ("Service arming call failed: %s"%e)

        # Similarly delacre other service proxies 
    def offboard_set_mode(self):
        # Call /mavros/set_mode to set the mode the drone to OFFBOARD
        # and print fail message on failure
        rospy.wait_for_service('mavros/set_mode')
        try:
            setMode=rospy.ServiceProxy('mavros/set_mode',mavros_msgs.srv.SetMode)
            result=setMode(custom_mode='OFFBOARD')
            #print("set mode to offboard")
            #print(result)
        except rospy.ServiceException as e:
            print ("Service offvoard set_mode call failed: %s"%e)
                
    def setAutoLandMode(self):
        rospy.wait_for_service('mavros/set_mode')
        try:
            flightModeService = rospy.ServiceProxy('mavros/set_mode', mavros_msgs.srv.SetMode)
            flightModeService(custom_mode='AUTO.LAND')
        except rospy.ServiceException as e:
            print("service set_mode call failed: %s. Autoland Mode could not be set."%e)

    def set_parameter(self,paramId='COM_RCL_EXCEPT',set_param_value_integer=2,set_param_value_real=2.0):
        rospy.wait_for_service('mavros/param/set')
        try:
            setParams=rospy.ServiceProxy('mavros/param/set',mavros_msgs.srv.ParamSet)
            paramValue= ParamValue()
            paramValue.real=set_param_value_real
            response=setParams(param_id=paramId,value=paramValue)
            #print("Done here!!")
            print("setting parameter", paramId , response.success , response.value.real)
        except rospy.ServiceException as e:
            print("Service  set_Parameters call failed: %s"%e)
    def activateGripper(self, setValue=True):
        print("trying to activate Gripper")
        rospy.wait_for_service("/activate_gripper")
        try:
            gripper = rospy.ServiceProxy('/activate_gripper', Gripper )
            result = gripper(activate_gripper=setValue)
            print("result of activaGripper : " , result)
            return result
        except rospy.ServiceException as e:
            print("service activaGripper call failed: %s. Autoland Mode could not be set."%e)
    def TAKE_OFF(self):
        #latitude = 0,longitude = 0
        print("TAKING OFF!!!!")
        rospy.wait_for_service('mavros/cmd/takeoff')
        try:
            takeoffService = rospy.ServiceProxy('/mavros/cmd/takeoff', mavros_msgs.srv.CommandTOL)
            takeoffService(altitude = 3, latitude=0,longitude=0, min_pitch=0, yaw=0)
        except rospy.ServiceException as e:
            print ("Service takeoff call failed: %s" %e)
    def LAND(self,x,y,z):
        print("Landing !!!!")
        rospy.wait_for_service('mavros/cmd/land')
        try:
            landService = rospy.ServiceProxy('/mavros/cmd/land', mavros_msgs.srv.CommandTOL)
            result = landService(altitude=z)
            print(result.success , result.result)
        except rospy.ServiceException as e:
            print ("Service land call failed: %s" %e)
    def TAKEOFF(self,z=3):
        print("TakeOff !!!!")
        rospy.wait_for_service('mavros/cmd/takeoff')
        try:
            takeoffService = rospy.ServiceProxy('/mavros/cmd/takeoff', mavros_msgs.srv.CommandTOL)
            result = takeoffService(altitude=z)
            print(result.success , result.result)
        except rospy.ServiceException as e:
            print ("Service takeoff call failed: %s" %e)
        
class stateMoniter:
    def __init__(self):
        self.state = State()
        # Instantiate a setpoints message
        self.positionX=0
        self.positionY=0
        self.positionZ=0
        self.isGripperCheck=False

    def stateCb(self, msg):
        # Callback function for topic /mavros/state
        self.state = msg
    def setPosition(self ,data):
        #to keep track of drone position
        self.positionX=data.pose.position.x
        self.positionY=data.pose.position.y
        self.positionZ=data.pose.position.z
    def gripperCheck(self, data):
        if data.data == 'True':
            self.isGripperCheck=True
        else:
            self.isGripperCheck=False


#this function will try to reach the point declared
#this will also take allowable error so we adjust the approx level
def goToPoint( target, stateMt, local_pos_pub,rate, pos=PoseStamped() , absoluteErrorMargin=(0.2,0.2,0.2) ):
    tarX,tarY,tarZ=target
    pos.pose.position.x, pos.pose.position.y, pos.pose.position.z  = tarX,tarY,tarZ
    currX,currY,currZ=stateMt.positionX,stateMt.positionY,stateMt.positionZ
    print("the target is" , target, "curr position is : " ,currX,currY,currZ )
   

    local_pos_pub.publish(pos)
    rate.sleep()
    abs1,abs2,abs3=absoluteErrorMargin
    #waiting till drone goes in allowable range
    while  not rospy.is_shutdown():
        currX,currY,currZ=stateMt.positionX,stateMt.positionY,stateMt.positionZ
        if (abs(tarX-currX) < abs1 and abs(tarY-currY) < abs2 and abs(tarZ-currZ)<abs3):
            break
    print( "current position is :", stateMt.positionX,stateMt.positionY,stateMt.positionZ , "target was : ", target) 
    rate.sleep() 
    print()

#this function can be used to arm the drone or setting mode to OFFBOARD mode
def armingDrone(local_pos_pub,stateMt,ofb_ctl,rate, position=(0,0,0)):
    pos =PoseStamped()
    pos.pose.position.x = position[0]
    pos.pose.position.y = position[1]
    pos.pose.position.z = position[2]

    countC=0
    for i in range(100):
        local_pos_pub.publish(pos)
        countC+=1
        rate.sleep()
    while not stateMt.state.armed:               #checking if it is already armed or not
        ofb_ctl.setArm()
        rate.sleep()
        print("Arming!!")
    while not stateMt.state.mode=="OFFBOARD":
        ofb_ctl.offboard_set_mode()
        #print(stateMt.state.mode)
        rate.sleep()
        print ("OFFBOARD mode being activated")


def main():


    stateMt = stateMoniter()
    ofb_ctl = offboard_control()

    # Initialize publishers
    local_pos_pub = rospy.Publisher('mavros/setpoint_position/local', PoseStamped, queue_size=10)
    
    # Specify the rate 
    rate = rospy.Rate(20.0)

    pos =PoseStamped()
    pos.pose.position.x = 0
    pos.pose.position.y = 0
    pos.pose.position.z = 0

    # Initialize subscriber 
    rospy.Subscriber("/mavros/state",State, stateMt.stateCb)
    rospy.Subscriber("/mavros/local_position/pose", PoseStamped, stateMt.setPosition)
    rospy.Subscriber("/gripper_check",std_msgs.msg.String , stateMt.gripperCheck )
    
    #setting parameters
    ofb_ctl.set_parameter('COM_DISARM_LAND',set_param_value_real= 10.0)
    ##########################################################################################################################################################
    #arming the Drone and setting it in OFFBOARD MODE
    armingDrone(local_pos_pub,stateMt,ofb_ctl,rate)
    
    bottomZ = stateMt.positionZ
    print(bottomZ)
    
    #moving drone
    #TakingOff upto 3 meter
    #"Takeoff and the initial position to the height of 3m"
    goToPoint((0,0,3),stateMt,local_pos_pub,rate,pos, (0.15,0.15,0.15))
    goToPoint((3,0,3),stateMt,local_pos_pub,rate,pos , (0.2,0.15,0.2))
    goToPoint((3,0.2,0),stateMt,local_pos_pub,rate,pos , (0.15,0.15,0.15)) #just being safe and for soft landing


    #-------------------------------------------LANDING AND PICKING UP THE BOX---------------------------------------------------------------------
    #"Land on the box and pick the box"
    ofb_ctl.setAutoLandMode()       #LANDING
    print( "current position is :", stateMt.positionX,stateMt.positionY,stateMt.positionZ ) 
    
    while not stateMt.isGripperCheck:       #Cheking if we are ready to pick up
        rate.sleep()
    print( "current position is :", stateMt.positionX,stateMt.positionY,stateMt.positionZ ) 
    
    rospy.sleep(3)                         #waiting for some time

    print( "current position is :", stateMt.positionX,stateMt.positionY,stateMt.positionZ ) 
    print()
    if stateMt.isGripperCheck:
        result = ofb_ctl.activateGripper(True)
        print("succes to catch gripper : " ,result)

    #--------------------------------------------------------------------------------------------------------------------
    
    
    #setting mode to OFFBOARD
    armingDrone(local_pos_pub,stateMt,ofb_ctl,rate,position=(0,0,0))
    
    goToPoint((3,0,3),stateMt,local_pos_pub,rate,pos,(0.15,0.15,0.15))
    goToPoint((3,3,3),stateMt,local_pos_pub,rate,pos, (0.2,0.2,0.2))
    goToPoint((3,3,0),stateMt,local_pos_pub,rate,pos, (0.15,0.15,0.15))
    


    #----------------------------------------------------LANDING AND DROPPING THE BOX-------------------------------------------------------------------
    ofb_ctl.setAutoLandMode()
    print( "current position is :", stateMt.positionX,stateMt.positionY,stateMt.positionZ ) 
    
    rospy.sleep(5)                         #waiting for some time

    print( "current position is :", stateMt.positionX,stateMt.positionY,stateMt.positionZ ) 
    print()
    if stateMt.isGripperCheck:
        ofb_ctl.activateGripper(False)
        print("succes to leave gripper : " ,result)
    #--------------------------------------------------------------------------------------------------------------------



    #setting mode to OFFBOARD
    armingDrone(local_pos_pub,stateMt,ofb_ctl,rate,position=(0,0,0))
        
    goToPoint((3,3,3),stateMt,local_pos_pub,rate,pos,(0.15,0.15,0.15))
    goToPoint((0,0,3),stateMt,local_pos_pub,rate,pos)

    #LANDING THE BOX
    ofb_ctl.setAutoLandMode()
    while  stateMt.positionZ > 0:
        rate.sleep()
    rospy.sleep(11)
    print( "LANDING position is :", stateMt.positionX,stateMt.positionY,stateMt.positionZ )
    if stateMt.state.armed :
        ofb_ctl.setArm(False)

if __name__ == '__main__':
    try:
        main()
    except rospy.ROSInterruptException:
        print("Errror!!")
        pass