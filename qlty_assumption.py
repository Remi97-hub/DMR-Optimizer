import copy

def get_name_level(society_count:int):
    society_details={}
    for i in range(society_count):
        society_name=str(input("Please enter Society name:"))
        society_level=str(input("Please enter Society level('highest','higher','high','average','below average','low','lowest'):"))
        society_details[society_name]=[society_level]
    return society_details

def SNF_level_pipeline(overall_snf: float, level: str):
   
    level_adjustments = {
        "highest": 0.3,
        "higher": 0.2,
        "high": 0.1,
        "average": 0.0,
        "below average": -0.1,
        "low": -0.2,
        "lowest": -0.3
    }
    
    adj = level_adjustments.get(level.lower())
    
    if adj is None:
        print("Please Check the Spelling!!!")
        return None
    
    m = overall_snf + adj
    
    
    m = max(m, 7.7)
    
    return round(m, 1)

def Fat_level_pipeline(overall_fat: float, level: str):
    level_adjustments = {
        "highest": 0.2,
        "higher": 0.1,
        "high": 0.0,
        "average": -0.1,
        "below average": -0.2,
        "low": -0.3,
        "lowest": -0.4
    }
    
    adj = level_adjustments.get(level.lower())
    
    if adj is None:
        print("Please Check the Spelling!!!")
        return None
    
    m = overall_fat + adj
    m = max(m, 3.3)
    
    return round(m, 1)

def set_W_assumption(society_details: dict, Overall_qlty: float, quantities: dict,level_pipeline):
    total_qty = 0
    #W_stage1 = 0.000

    details=copy.deepcopy(society_details)
    for key in details.keys():
        qty = quantities[key]  
        level = details[key][0]
        qlty = round(level_pipeline(Overall_qlty, level), 1)
        
        #w_qlty = round((qty * qlty) / 100, 3)
        
        details[key].append(qty)      
        details[key].append(qlty) 
        #details[key].append(w_qlty)    
        
        total_qty += qty
        #W_stage1 += w_qlty
        
    overall_Wqlty = round((total_qty * Overall_qlty) / 100, 3)
    #difference_stage1 = round(overall_Wqlty - W_stage1, 3)

    return details, overall_Wqlty, total_qty

def qlty_wqlty(society_details,x):
    details=copy.deepcopy(society_details)
    for key,q in zip(details.keys(),x):
        details[key][2]=float(q/10)
        wq=round(details[key][1]*details[key][2]/100,3)
        details[key].append(wq)
    return details