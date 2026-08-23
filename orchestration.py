from qlty_assumption import get_name_level,SNF_level_pipeline,Fat_level_pipeline,set_W_assumption,qlty_wqlty
from qlty_optimization import solve_qlty_nudge
from final_data_output import create_society_summary_report

total_society=int(input("Please enter the total number of Societies:"))
society_details=get_name_level(total_society)

try:
    Overall_fat = float(input("Please Enter the Overall Fat: "))
    Overall_SNF = float(input("Please Enter the Overall SNF: "))
except ValueError:
    print("Invalid float input. Setting default to 0.0")
    Overall_fat = 0.0
    Overall_SNF = 0.0
    
quantities = {}
for key in society_details.keys():
    while True:
        try:
            qty = int(input(f"Please enter the {key} Quantity: "))
            quantities[key] = qty
            break 
        except ValueError:
            print("Invalid input! Quantity must be a whole number (integer).")

#weight assumption
society_details_f,overall_Wfat,total_qty=set_W_assumption(society_details,Overall_fat,quantities,Fat_level_pipeline) 
society_details_snf,overall_Wsnf,total_qty=set_W_assumption(society_details,Overall_SNF,quantities,SNF_level_pipeline)

#qty seperation for constant c
qty=[i[1] for i in society_details_f.values()]

#decision variables x for fat and snf
fat_pre=[i[2]*10 for i in society_details_f.values()]
snf_pre=[i[2]*10 for i in society_details_snf.values()]

#target fixation for fat and snf
target_f=overall_Wfat*1000
f_target_low=target_f-1
f_target_high=target_f+1

target_snf=overall_Wsnf*1000
snf_target_low=target_snf-1
snf_target_high=target_snf+1


#MILP
x_f,res_f=solve_qlty_nudge(qty, fat_pre, f_target_low, f_target_high, max_step=2)
x_snf,re_snf=solve_qlty_nudge(qty, snf_pre, snf_target_low, snf_target_high, max_step=2)

#Quality and weighted quality calculation
society_details_f=qlty_wqlty(society_details_f,x_f)
society_details_snf=qlty_wqlty(society_details_snf,x_snf)

#conversion into df for operational usage
report=create_society_summary_report(society_details_f, society_details_snf)
print(report)