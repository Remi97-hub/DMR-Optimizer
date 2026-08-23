import pandas as pd
from datetime import date

def create_society_summary_report(society_details_f: dict, society_details_snf: dict):
    data_rows = []
    total_qty = 0
    total_wf = 0.0
    total_wsnf = 0.0

    for key in society_details_f:
        qty = society_details_f[key][1]
        
        fat = society_details_f[key][2]
        wf = society_details_f[key][3]
        
        snf = society_details_snf[key][2]
        wsnf = society_details_snf[key][3]
        
        t_s = round(fat + snf, 2)
        weighted_avg = round(wf + wsnf, 3) 
        
        data_rows.append([key, qty, fat, snf, t_s, wf, wsnf, weighted_avg])
        
        total_qty += qty
        total_wf += wf
        total_wsnf += wsnf

    total_wf = round(total_wf, 3)
    total_wsnf = round(total_wsnf, 3)
    total_wavg = round(total_wf + total_wsnf, 3)

    overall_fat = round((total_wf * 100) / total_qty, 2) if total_qty > 0 else 0
    overall_snf = round((total_wsnf * 100) / total_qty, 2) if total_qty > 0 else 0
    overall_ts = round(overall_fat + overall_snf, 2)

    final_rows = []
    final_rows.extend(data_rows)
    
    final_rows.append(['Total', total_qty, overall_fat, overall_snf, overall_ts, total_wf, total_wsnf, total_wavg])
    final_rows.append(['', '', '', '', '', '', '', '']) # Visual spacer
    
    final_rows.append(['Summary Breakdown:', '', '', '', '', '', '', ''])
    final_rows.append(['Overall Fat:', overall_fat, '', 'Total Weighted Fat:', total_wf, '', '', ''])
    final_rows.append(['Overall SNF:', overall_snf, '', 'Total Weighted SNF:', total_wsnf, '', '', ''])
    final_rows.append(['Overall T.S:', overall_ts, '', 'Overall Weighted Avg:', total_wavg, '', '', ''])

    columns = ['Name', 'Qty', 'Fat', 'SNF', 'T.S', 'Weighted Fat', 'Weighted SNF', 'Weighted Average']
    df = pd.DataFrame(final_rows, columns=columns)
    df.set_index('Name', inplace=True)
    
    current_date = date.today().strftime("%B %d, %Y")
    df.columns.name = f"Date: {current_date}"
    

    pd.set_option('display.expand_frame_repr', False)
    
    return df


