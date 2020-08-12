_7AOnOffbody = {
  "query": {
    "bool": {
      "minimum_should_match": 1,
      "should": [
        {
          "bool": {
            "minimum_should_match": 2,
            "should": [
              {
                "match_phrase": {
                  "iName": {
                    "query": "OnUserRequest"
                  }
                }
              },
              {
                "match": {
                  "msg": {
                    "query": "relay"
                  }
                }
              }
            ]
          }
        },
        {
          "match_phrase": {
            "M": "got state report"
          }
        },
        {
          "bool":{
            "minimum_should_match": 2,
            "should":[
              {
                "match_phrase": {
                  "url": "thirdparty"
                }
              },
              {
                "match": {
                  "url": {
                    "query":"on off"
                  }
                }
              }
            ]
          }
        },
        {
          "match_phrase": {
            "M": "trigger"
          }
        },
        {
          "match_phrase": {
            "M": "got timer event report"
          }
        },
        {
          "bool":{
            "minimum_should_match": 2,
            "should":[
              {
                "match_phrase": {
                  "iName": "deviceStatusPost"
                }
              },
              {
                "match":{
                  "M":{
                    "query":"request"
                  }
                }
              }
            ]
          }
        },
        {
          "match_phrase": {
            "msg": "\"otp\":\"on\""
          }
        }
      ]
    }
  }
}