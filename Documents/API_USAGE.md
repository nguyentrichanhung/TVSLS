# API DOCUMENTS FOR TVS
---
# Table of Contents
- [I. General API Information](#i-general-api-information)
    * [I.1 HTTP Return Codes](#i1-http-return-codes)
    * [I.2 GENERAL INFORMATION ON ENDPOINTS](#i2-general-information-on-endpoints)
- [II. Update Note](#ii-update-note)
    * [1. UPDATE NOTE (10/0/2021)](#1-update-note-10102021)
- [III. Code Return](#iii-code-return)
- [IV. API USAGE](#iv-api-usage)
    * [1 User Management API](#1-user-management-api)
    * [2 Device Management API](#2-device-management-api)
    * [3. LANE PROPERTIES](#3-lane-properties)
    * [4. COMMON CONFIGS](#4-common-configs)
    * [5. HEALTH CHECK MONITOR](#5-health-check-monitor)
    * [6. STREAMING API](#6-streaming-api)
----
## I General API Information

- The base endpoint is: http://192.168.0.5:5500
- All enpoints return eithere a JSON object, array or image in binary
- All time and timestampp related fields are follow Korea/Vietnam UTC time format
---
### I.1 HTTP Return Codes
- ```HTTP``` 400 return code are bad requests
- ```HTTP``` 401 return code are used for malformed requests, the issue is on the sender's side.
- ```HTTP``` 405 return code is unauthorized request
- ```HTTP``` 200 return code is used for successful request
- ```HTTP``` 201 return code is created successful request
-  ```HTTP``` 206 return code is  the request has succeeded and the body contains the requested ranges of data
- ```HTTP``` 5xx  return codes are used for internal errors; the issue is on server's side. It is important to NOT treat this as a failure operation;
---
## I.2 GENERAL INFORMATION ON ENDPOINTS
- For ```GET``` endpoints, parameter mus be sent as a ```query string```
  
- For ```POST```, ```PUT``` and ```DELETE``` endpoints, the parameters may be sent as a ```query string``` or in ```request body``` with content type ```apllication/json```
- Paramaters may be sent in any order.
- If a parameter sent in both the ```query string``` and ```request body```, the ```query string``` parameter will be used.
---
## II UPDATE NOTE
### ```1. UPDATE NOTE (10/10/2021)```
- Implement CRUD APIs for user management module
- Implement CRUD APIs Config management module
- Implement CRUD APIs Lane properties management module
- Implement Authorize process for all APIs
- Update Internal process with core algorithm
- Clean the source code and fix bug
---
## III. CODE RETURN

> code ```1000```: Request Done
> 
> code ```1001```: Request Fail
> 
> code ```1002```: Data is invalid in database
> 
> code ```1003```: Video is processing
>
> code ```1004```: Partial or empty data return
> 
> code ```1005```: Unauthorize return
----
## IV. API USAGE
----
### 1 User Management API


#### ADD USER

- Create POST request to create new user( only admin user can add the user)
```
POST /user/add_user
```

```
Request Header
Authorization: Bearer
Type: application/json
```

```json
Request: {
    "name" : "str",
	"role" : "str",
	"password": "str"
}

Response: {
  "message": "str",
  "success": "boolean"
}


```

*```Note```: The password rule: password must contain both lower and upper letter and at least special sysbol is required (!,@,#,$,%,^,&,*)

---
#### LOGIN
- Create POST request to login the local system
```
POST /login
```

```
Request Header
Authorization: No
Type: application/json
```

```json
Request: {
    "name" : "str",
	"password": "str"
}

Response: {
  "data": "str", //authorize token
  "message": "str",
  "success": "boolean"
}

```
*```Note```: Each token will have expired time 24 hours. After 24 hours the user will need to login again to access another APIs*

---
#### CHANGE PASSWORD

- Create POST request to change the password of user (current user or admin user can update the password)
```
POST /user/update_password
```

```
Request Header
Authorization: Bearer
Type: application/json
```

```json
Request: {
    "user_id" : "str", //only require when change by admin user
	"password": "str"
}

Response: {
  "message": "str",
  "success": "boolean"
}
```
---
#### UPDATE ROLE

- Create POST request to change the role of user ( admin user can update the password)
```
POST /user/update_role
```

```
Request Header
Authorization: Bearer
Type: application/json
```

```json
Request: {
    "user_id" : "str",
	"role": "str"
}

Response: {
  "message": "str",
  "success": "boolean"
}
```
---
### 2 Device Management API

#### CREATE DEVICE

- Create POST request to create new device( only admin user can add the user)
```
POST /device
```

```
Request Header
Authorization: Bearer
Type: application/json
```

```json
Request: {
	"device" : {
		"type" : "str",
		"name" : "str",
		"location": {
						"lat": "",
            "long": ""
		},
		"region" : "str",
		"meta_data" : {
			"ip" : "str",
			"http_port" : "str",
			"rtsp_port" : "str",
			"user" : "str",
			"password" : "str"
		}
	}
}

Response: {
  "data": "str", //device_id
  "message": "str",
  "success": "boolean"
}


```
----
#### GET DEVICE

- Create GET request to create new user( only admin user can add the user)
```
GET /device/<device_id>
```

```
Request Header
Authorization: Bearer
Type: application/json
```

```json
Request: None

Response: {
  "data": {
	"device" : {
        "id" : "str",
		"type" : "str",
		"name" : "str",
		"location": {
						"lat": "",
            "long": ""
		},
		"region" : "str",
		"meta_data" : {
			"ip" : "str",
			"http_port" : "str",
			"rtsp_port" : "str",
			"user" : "str",
			"password" : "str"
		}
	}
    },
    "message" : "str",
    "success" : "boolean"
}
```
----
#### EDIT DEVICE

- Create POST request to edit the exsit device( only admin user can add the device)
```
POST /device/<device_id>
```

```
Request Header
Authorization: Bearer
Type: application/json
```

```json
Request: {
	"device" : {
		"type" : "str",
		"name" : "str",
		"location": {
						"lat": "",
            "long": ""
		},
		"region" : "str",
		"meta_data" : {
			"ip" : "str",
			"http_port" : "str",
			"rtsp_port" : "str",
			"user" : "str",
			"password" : "str"
		}
	}
}

Response: {
  "message": "str",
  "success": "boolean"
}
```
---

### 3. LANE PROPERTIES

#### ADD LANES

- Create POST request to create lane properties( only admin user and police user can add the lane)
```
POST /configs/lanes
```

```
Request Header
Authorization: Bearer
Type: application/json
```

```json
Request: {
	"device_id" : "str",
	"lanes" : {
		"lane1" : {
			"name" : "str",
			"vehicle_properties" : {
                "1": {
                        "speed_limit" : "int",
                        "type" : "str"
                    },
                "2" :  {
                        "speed_limit" : "int",
                        "type" : "str"
                    }
							},
			"direction" : "str",
			"points" : "array" // list of points
		}
	}
}

Response: {
  "message": "str",
  "success": "boolean"
}
```
----

#### GET LANE PROPERTIS
- Create GET request to get the list of lane config
```
GET /configs/lanes
```

```
Request Header
Authorization: Bearer
Type: application/json
```

```json
Request: None

Response:{
  "data": {
    "code": 1000,
    "data": [
      {
        "created_at": "timestamp",
        "deleted_at": null,
        "device_id": "str",
        "direction": "str",
        "id": "str",
        "name": "str",
        "points": "array",
        "updated_at": "timestamp",
        "vehicle_properties": {
          "1": {
            "speed_limit": "int",
            "type": "str"
          },
          "2": {
            "speed_limit": "int",
            "type": "str"
          }
        }
      }
    ],
    "message": "str"
  },
  "message": "str",
  "success": false
}
```
---

#### UPDATE LANE PROPERTIES

- Create PATCH request to update lane properties( only admin user and police user can update the lane)
```
PATCH /configs/lanes
```

```
Request Header
Authorization: Bearer
Type: application/json
```

```json
Request: {
	"device_id" : "str",
	"lanes" : {
		"lane1" : {
			"name" : "str",
			"vehicle_properties" : {
                "1": {
                        "speed_limit" : "int",
                        "type" : "str"
                    },
                "2" :  {
                        "speed_limit" : "int",
                        "type" : "str"
                    }
							},
			"direction" : "str",
			"points" : "array" // list of points
		}
	}
}

Response: {
  "message": "str",
  "success": "boolean"
}
```
*```Note```: lane1 is the key name so if we have many lanes we just increase the number lane2,lane3,. for key value*

---
### 4. COMMON CONFIGS

#### ADD CONFIGS

- Create POST request to create common configs ( only admin user and police user can add the lane)
```
POST /configs/common
```

```
Request Header
Authorization: Bearer
Type: application/json
```

```json
Request: {
	"device_id" : "str",
	"videos" : {
		"resolution" : {
			"width" : "int",
			"height" : "int"
		},
		"fps" : "int",  // frame per second
		"dbe" : "int",  // duration before event
		"extension" : "str"
	},
	"stream" : {
				"resolution" : {
			"width" : "int",
			"height" : "int"
		},
		"channel" : "str" // each camera have 3 channels
	}
}

Response: {
  "message": "str",
  "success": "boolean"
}
```

*```Note```: the maximum for dbe is 5-7 seconds*

----
#### GET COMMON CONFIG
- Create GET request to get the common config
```
GET /configs/common
```

```
Request Header
Authorization: Bearer
Type: application/json
```

```json
Request: None

Response:{
  "data": {
    "code": 1000,
    "data": {
      "config_data": {
		"videos": {"resolution" : {
			"width" : "int",
			"height" : "int"
		},
		"fps" : "int",  // frame per second
		"dbe" : "int",  // duration before event
		"extension" : "str"
	    },
        "stream" : {
				"resolution" : {
			"width" : "int",
			"height" : "int"
		},
		"channel" : "str" // each camera have 3 channels
	}
      },
      "created_at": "timestamp",
      "deleted_at": "None",
      "device_id": "str",
      "id": "str",
      "updated_at": "timestamp"
    },
    "message": "str"
  },
  "message": "str",
  "success": "boolean"
}
```
---

#### UPDATE COMMON CONFIG


- Create PATCH request to update common configs ( only admin user and police user can add the lane)
```
PATCH /configs/common
```

```
Request Header
Authorization: Bearer
Type: application/json
```

```json
Request: {
	"device_id" : "str",
    "config_id" : "str",
	"videos" : {
		"resolution" : {
			"width" : "int",
			"height" : "int"
		},
		"fps" : "int",  // frame per second
		"dbe" : "int",  // duration before event
		"extension" : "str"
	},
	"stream" : {
				"resolution" : {
			"width" : "int",
			"height" : "int"
		},
		"channel" : "str" // each camera have 3 channels
	}
}

Response: {
  "message": "str",
  "success": "boolean"
}
```

---
### 5. HEALTH CHECK MONITOR

#### GET CPU INFORMATION

- Create GET request to get the common config
```
GET /system/cpu
```

```
Request Header
Authorization: Bearer
Type: application/json
```

```json
Request: None

Response:{
  "data": {
      "processor" : {
          "physicals" : "int",
          "logicals" : "int",
          "usage" : "str", //percent value per cpu
          "usages" : "str" //whole cpu
      },
      "memory" : {
          "total" : "int",
          "available" : "int",
          "used" : "int",
          "free" : "int",
          "percent" : "str"
      },
      "storage" : {
        "total" : "int",
        "available" : "int",
        "used" : "int",
        "free" : "int",
        "percent" : "str"
      }
   },
    "message": "str"
  },
  "message": "str",
  "success": "boolean"
}
```
----
#### GPU CHECK

*```to-do```*

---
### 5. Control System

#### START SYSTEM

- Create GET request to start internal process
```
GET /system/start
```

```
Request Header
Authorization: Bearer
Type: application/json
```

```json
Request: None

Response:{
  "message": "str",
  "success": "boolean"
}
```
---

### 6. STREAMING API
---
#### STREAM WITH SINGLE CAMERA
- this URL is created to get streaming after detection from cameras
```
GET: /stream_feed
```
> Note : The current version only works for one cameras, we will update more for multiple cameras for the next version
---
#### STREAM WITH VIDEOS ( TEST PURPOSE )
- this is created for testing the performance of detection on video
```
GET: /video_feed/<video_name>
```
```video_name``` : video1 , video2, video3, video4, video5, video6, video7, video8, video9 are avaiable
> Note: we can not access live stream and open video as same time since the current data flow not allow to work with multiple process detection