import re

class parse():
  @staticmethod
  def parse_create_table(sql):
    match=re.match(
        r"CREATE TABLE (\w+) \((.*)\)",sql,re.IGNORECASE
    )

    if not match:
        print("❌ Invalid CREATE format")
        return None
    
    table_name=match.group(1)
    columns_str=match.group(2)

    columns={}
    index_hints = {}
    print(f"\n🔍 PARSER DEBUG:")  # ← ADD THIS
    print(f"   Raw SQL: {sql}")
    for col_def in columns_str.split(","):
        parts=col_def.strip().split()
        print(f"   Column def: {col_def}")  # ← ADD THIS
        print(f"   Parts: {parts}")
        if len(parts)==2:
            col_name,col_type=parts
            columns[col_name]=col_type.upper()
        elif len(parts) == 3:
          col_name, col_type, hint = parts
          columns[col_name] = col_type.upper()
          index_hints[col_name] = hint.upper()
          print(f"   → Saved hint: {col_name} = {hint.upper()}")
        else:
          print(f"❌ Invalid column: {col_def}")
          return None
    print(f"   Final columns: {columns}")  # ← ADD THIS
    print(f"   Final hints: {index_hints}")
    
    return{
        "type":"CREATE",
        "table":table_name,
        "columns":columns,
        "index_hints": index_hints if index_hints else None
    }
  @staticmethod
  def parse_insert(sql):
    match=re.match(
        r"INSERT INTO (\w+) VALUES\s+(.+)",sql,re.IGNORECASE
    )

    if not match:
        print("❌ Invalid INSERT format")
        return None
    
    table_name=match.group(1)
    values_str=match.group(2).strip()

    row_pattern = r"\(([^)]+)\)"
    row_matches = re.findall(row_pattern, values_str)
    if not row_matches:
        print("❌ No values found")
        return None

    all_rows=[]
    for row_str in row_matches:
        values = []
        
        for val in row_str.split(","):
            val = val.strip()
            
            if val.startswith("'") and val.endswith("'"):
                val = val[1:-1]  
            elif val.startswith('"') and val.endswith('"'):
                val = val[1:-1] 
            
            values.append(val)
        
        all_rows.append(values)

    return{
        "type":"INSERT",
        "table":table_name,
        "values":all_rows
    }
  @staticmethod
  def parse_insert_col(sql):
     match=re.match(
        r"INSERT COLUMNS INTO (\w+) \((.*)\)",sql,re.IGNORECASE
     )
     if not match:
        print("❌ Invalid INSERT COL format")
        return None
     table=match.group(1)
     columns_str=match.group(2)

     columns={}
     for col_def in columns_str.split(","):
        parts=col_def.strip().split()
        if len(parts)==2:
            col_name,col_type=parts
            columns[col_name]=col_type.upper()
     return{
        "type":"INSERT COL",
        "table":table,
        "columns":columns
    }
  @staticmethod
  def parse_add_column(sql):
     match=re.match(
        r"ADD COLUMNS INTO (\w+) \((.*)\)",sql,re.IGNORECASE
     )

     if not match:
        print("❌ Invalid ADD COL format")
        return None
    
     table=match.group(1)
     columns_str=match.group(2)

     columns={}
     index_hints = {} 
     for col_def in columns_str.split(","):
        parts=col_def.strip().split()
        if len(parts)==2:
            col_name,col_type=parts
            columns[col_name]=col_type.upper()
        elif len(parts) == 3:
            col_name, col_type, hint = parts
            columns[col_name] = col_type.upper()
            index_hints[col_name] = hint.upper()
        else:
            print(f"❌ Invalid column definition: {col_def}")
            return None
     return{
        "type":"ADD COL",
        "table":table,
        "columns":columns,
        "index_hints": index_hints if index_hints else None
    }
  
  @staticmethod
  def parse_distinct_col(sql):
     match=re.match(
        r"SELECT\s+DISTINCT\s+ON\s*\(\s*([^)]+)\s*\)\s+(.+?)\s+FROM\s+(\w+)(?:\s+ORDER\s+BY\s+(.+))?",sql,re.IGNORECASE
     )
     if not match:
        print("❌ Invalid DISTINCT ON format")
        return None
     distinct_cols_str = match.group(1)
     select_cols_str = match.group(2)
     table_name = match.group(3) 
     order_by_str = match.group(4)

     distinct_columns = [col.strip() for col in distinct_cols_str.split(",")]

     if select_cols_str.strip() == "*":
        select_columns = "*"
     else:
        select_columns = [col.strip() for col in select_cols_str.split(",")]
     order_by = []
     
     if order_by_str:
        order_parts = order_by_str.split(",")
        
        for part in order_parts:
            part = part.strip()
            
            # Check for DESC
            if "DESC" in part.upper():
                # Remove DESC and extract column name
                col = part.upper().replace("DESC", "").strip()
                order_by.append({
                    "column": col.lower(),
                    "direction": "DESC"
                })
            
            elif "ASC" in part.upper():
                col = part.upper().replace("ASC", "").strip()
                order_by.append({
                    "column": col.lower(),
                    "direction": "ASC"
                })
            
           
            else:
                order_by.append({
                    "column": part.lower(),
                    "direction": "ASC"
                })
    
     return {
        "type": "DISTINCT",
        "distinct": distinct_columns,
        "select_col": select_columns,
        "table": table_name,
        "order_by": order_by 

    }
  @staticmethod
  def parse_upd_col(sql):
     match=re.match(
        r"UPDATE\s+(\w+)\s+TYPE\s+(INT|FLOAT|STR)\s+IN\s+(\w+)",sql,re.IGNORECASE
     )
     if not match:
        print("❌ Invalid UPDATE COL format")
        return None
     column=match.group(1)
     new_type=match.group(2).upper()
     table=match.group(3)

     return {
        "type": "UPDATE COL",
        "column": column,
        "new_type": new_type,
        "table": table
    }
  
   
  @staticmethod
  def parse_csv(sql):
    match=re.match(
        r"INSERT\s+FROM\s+(['\"]?)([^'\";\s]+\.csv)\1\s+INTO\s+(\w+)",sql,re.IGNORECASE
        
    )
    if not match:
        print("❌ Invalid INSERT CSV format")
        return None
    
    table_name=match.group(2).strip()
    csv_file=match.group(3).strip()

    return{
        "type": "CSV",
        "table":table_name,
        "csv_file":csv_file

    }
  @staticmethod
  def parse_excel(sql):
    match=re.match(
        r"INSERT\s+FROM\s+(['\"]?)(\S+\.xlsx)\1\s+INTO\s+(\w+)(?:\s+SHEET\s+(['\"]?)(\w+)\4)?",sql,re.IGNORECASE
    )
    if not match:
      print("❌ Invalid INSERT EXCEL format")
     
     
    table_name=match.group(3)
    excel_file=match.group(2)
    sheet=match.group(5)

    return{
        "type": "EXCEL",
        "table":table_name,
        "excel_file":excel_file,
        "sheet":sheet
    }
  @staticmethod
  def parse_show(sql):
     match=re.match(
        r"SHOW\s+PICKLE\s+FILE\s+OF\s+(\w+)",sql,re.IGNORECASE
    )
     if not match:
      print("❌ Invalid SHOW PICKLE format")
     table_name=match.group(1)
     return{
        "type": "SHOW",
        "table":table_name
    }
    
  @staticmethod
  def parse_drop(sql):
    match=re.match(
        r"DROP\s+(\w+)\s*",sql,re.IGNORECASE
    )

    if not match:
        print("❌ Invalid DROP format")
        return None
    
    table_name=match.group(1)

    return{
        "type": "DROP",
        "table":table_name
    }
  @staticmethod
  def parse_get(sql):
    match=re.match(
        r"SELECT\s+\*\s+FROM\s+(\w+)\s+WHERE\s+(\w+)\s*(>=|<=|!=|>|<|=)\s*(['\"]?)([^'\";\s]+)\4"
        ,sql,re.IGNORECASE
    )

    if not match:
        print("❌ Invalid WHERE format")
        return None
    
    table_name=match.group(1)
    col=match.group(2)
    op=match.group(3)
    value=match.group(5)

    return{
        "type": "WHERE",
        "table":table_name,
        "col":col,
        "op":op,
        "value":value
    }
  @staticmethod
  def parse_limit(sql):
    match=re.match(
        r"SELECT\s+(.+?)\s+FROM\s+(\w+)\s+LIMIT\s+(\d+)(?:\s+OFFSET\s+(\d+))?",sql,re.IGNORECASE
    )
    if not match:
        print("❌ Invalid LIMIT format")
        return None
    table=match.group(2)
    limit=match.group(3)
    offset=match.group(4)

    return{
        "type":"LIMIT",
        "table":table,
        "limit":limit,
        "offset":offset
    }
  @staticmethod
  def parse_update(sql):
    match = re.match(
        r"UPDATE\s+(\w+)\s+SET\s+(\w+)\s*=\s*(['\"]?)([^'\"=\s]+)\3\s+WHERE\s+(\w+)\s*([>=|<=|!=|>|<|=]+)\s*(['\"]?)([^'\"=\s]+)\7",
        sql,
        re.IGNORECASE)

    if not match:
     print("❌ Invalid UPDATE format")

    table_name = match.group(1)    
    upd_col = match.group(2)       
    upd_value = match.group(4)       
    where_col = match.group(5).strip()     
    op = match.group(6)      
    where_value = match.group(8).strip()
    
    return {
        "type": "UPDATE",
        "table_name": table_name,
        "upd_col": upd_col,
        "upd_value": upd_value,
        "where_col": where_col,
        "op": op,
        "where_value": where_value
    }
  @staticmethod
  def parse_deleterows(sql):
    match=re.match(
        r"DELETE\s+FROM\s+(\w+)\s+WHERE\s+(\w+)\s*([>=|<=|!=|>|<|=]+)\s*['\"]?([^'\";\s]+)['\"]?;?",
        sql,re.IGNORECASE
    )

    if not match:
        print("❌ Invalid WHERE DELETE format")
        return None

    table_name=match.group(1)
    col=match.group(2)
    op=match.group(3)
    value=match.group(4)

    return{
        "type": "DELETE",
        "table":table_name,
        "col":col,
        "op":op,
        "value":value
    }
  @staticmethod
  def parse_delete_allrows(sql):
    match=re.match(
        r"DELETE\s+(.+?)\s+ROWS OF\s+(\w+)",sql,re.IGNORECASE
    )
    if not match:
        print("❌ Invalid DELETE ROWS format")
        return None
    table_name=match.group(2)
    return{
     "type":"ALL",
     "table":table_name
 }
  @staticmethod
  def parse_delete_allcol(sql):
     match=re.match(
        r"DELETE\s+\*\s+COLUMNS\s+OF\s+(\w+)",sql,re.IGNORECASE
     )
     if not match:
        print("❌ Invalid DELETE COL format")
        return None
     table_name=match.group(1)
     return{
      "type":"ALL COL",
      "table":table_name
  }
  @staticmethod
  def parse_order_by_withcol(sql):
    match=re.match(
        r"SELECT\s+(.+?)\s+FROM\s+(\w+)\s+ORDER\s+BY\s+(\w+)(?:\s+LIMIT\s+(\d+))?(?:\s+OFFSET\s+(\d+))?",sql,re.IGNORECASE
    )
    if not match:
        print("❌ Invalid ORDER BY format")
        return None
    table=match.group(2)
    order=match.group(3)
    limit=match.group(4)
    offset=match.group(5)
    return{
        "type":"ORDER",
        "table":table,
        "order":order,
        "limit":limit,
        "offset":offset
    }
  @staticmethod
  def parse_group_by(sql):
    match=re.match(
        r"SELECT\s+(.+?)\s+FROM\s+(\w+)(?:\s+WHERE\s+(\w+)\s*([=<>!]+)\s*(['\"]?)(.+?)\5)?\s+GROUP\s+BY\s+(\w+)",sql,re.IGNORECASE
    )
    if not match:
        print("❌ Invalid GROUP BY format")
        return None
    columns_str = match.group(1).strip()
    table_name = match.group(2)
    where_col = match.group(3)
    where_op = match.group(4)
    where_value = match.group(6)
    group_by_column = match.group(7)

    columns = []
    aggregates = []

    col_parts = re.split(r',(?![^()]*\))', columns_str)

    for col in col_parts:
        col = col.strip()
        
        
        agg_match = re.match(r"(COUNT|SUM|AVG|MIN|MAX)\s*\(\s*(\*|\w+)\s*\)", col, re.IGNORECASE)
        
        if agg_match:
            func = agg_match.group(1).upper()
            field = agg_match.group(2)
            alias = f"{func}({field})"
            
            aggregates.append({
                "function": func,
                "column": field,
                "alias": alias
            })
        else:
           
            columns.append(col)
    
    result = {
        "type": "GROUP BY",
        "columns": columns,
        "aggregates": aggregates,
        "table": table_name,
        "group_by": group_by_column
    }
    if where_col:
        result["where_col"] = where_col
        result["where_op"] = where_op
        result["where_value"] = where_value
    
    return result
  @staticmethod
  def parse_order_by_full(sql):
    match=re.match(
        r"SELECT\s+(.+?)\s+FROM\s+(\w+)\s+ORDER\s+BY\s+(\w+)\s+(ASC|DESC)(?:\s+LIMIT\s+(\d+))?(?:\s+OFFSET\s+(\d+))?",sql,re.IGNORECASE
    )
    if not match:
        print("❌ Invalid ORDER BY format")
        return None
    table=match.group(2)
    order=match.group(3)
    dir=match.group(4).upper()
    limit=match.group(5)
    offset=match.group(6)
    return{
     "type":"FULL",
     "table":table,
     "order":order,
     "dir":dir,
     "limit":limit,
     "offset":offset
     
 }
 

  @staticmethod
  def parse_select(sql):
    match=re.match(
        r"SELECT\s+(.+?)\s+FROM\s+(\w+)" ,sql,re.IGNORECASE
    )

    if not match:
        print("❌ Invalid SELECT format")
        return None
    
    columns=match.group(1).strip()
    table_name=match.group(2)

    return{
     "type":"SELECT",
     "table":table_name,
     "columns":columns
 }
