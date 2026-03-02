from Storage.persistent_table_manager import PersistentTableManager as TableManager
from Storage.parse import parse

pr = parse()

# Global tm - will be overridden per user
tm = TableManager()

def execute_command(tm, parsed):
    if parsed is None:
        return
    
    cmd_type = parsed["type"]

    if cmd_type == "CREATE":
        tm.create_table(parsed["table"], parsed["columns"],parsed["index_hints"])
        return None

    elif cmd_type == "INSERT":
        tm.insert_rows(parsed["table"], parsed["values"])
        return None
    
    elif cmd_type == "INSERT COL":
        tm.insert_col(parsed["table"], parsed["columns"])
        return None
    
    elif cmd_type == "ADD COL":
        tm.addmore_col(parsed["table"], parsed["columns"],parsed["index_hints"])
        return None
    
    elif cmd_type == "UPDATE COL":
        tm.update_col(parsed["table"], parsed["column"], parsed["new_type"])
        return None

    elif cmd_type == "CSV":
        tm.read_csv(parsed["table"], parsed["csv_file"])
        return None

    elif cmd_type == "EXCEL":
        tm.insert_from_excel(parsed["table"], parsed["excel_file"], parsed["sheet"])
        return None

    elif cmd_type == "DROP":
        tm.delete(parsed["table"])
        return None

    elif cmd_type == "DELETE":
        result = tm.delete_row(parsed["table"], parsed["col"], parsed["op"], parsed["value"])
        return result if result else None
    
    elif cmd_type == "ALL":
        tm.delete_all_rows(parsed["table"])
        return None

    elif cmd_type == "ALL COL":
        tm.delete_all_col(parsed["table"])
        return None

    elif cmd_type == "DISTINCT":
        parse_dict = {
            "distinct": parsed["distinct"],
            "select_col": parsed["select_col"],
            "table": parsed["table"],
            "order_by": parsed["order_by"]
        }
        result = tm.distinc_on(parse_dict)
        return result if result else []

    elif cmd_type == "GROUP BY":
        where_filter = None
        if "where_col" in parsed:
            where_filter = {
                "col": parsed["where_col"],
                "op": parsed["where_op"],
                "value": parsed["where_value"]
            }
        result = tm.group_by(parsed["table"], parsed["group_by"], parsed["aggregates"], where_filter)
        return result if result else []
    
    elif cmd_type == "SHOW":
        result = tm.load_pickle(parsed["table"])
        return result

    elif cmd_type == "FULL":
        result = tm.order_by_full(parsed["table"], parsed["order"], parsed["dir"], parsed["limit"], parsed["offset"])
        return result if result else []

    elif cmd_type == "LIMIT":
        result = tm.limit(parsed["table"], parsed["limit"], parsed["offset"])
        return result if result else []

    elif cmd_type == "ORDER":
        result = tm.order_by_withcol(parsed["table"], parsed["order"], parsed["limit"], parsed["offset"])
        return result if result else []
        
    elif cmd_type == "UPDATE":
        result = tm.update_rows(parsed["table_name"], parsed["upd_col"], parsed["upd_value"], parsed["where_col"], parsed["op"], parsed["where_value"])
        return result if result else []

    elif cmd_type == "WHERE":
        result = tm.filter_rows(parsed["table"], parsed["col"], parsed["op"], parsed["value"])
        return result if result else []
        
    elif cmd_type == "SELECT":
        result = tm._print_table(parsed["table"])
        return result if result else []
    
    return None


def parse_sql(sql_command):
    sql_upper = sql_command.upper().strip()
    parsed = None
    
    if sql_upper.startswith("CREATE TABLE"):
        parsed = pr.parse_create_table(sql_command)
    
    elif sql_upper.startswith("INSERT FROM"):
        if ".CSV" in sql_upper:
            parsed = pr.parse_csv(sql_command)
        elif ".XLSX" in sql_upper:
            parsed = pr.parse_excel(sql_command)
    
    elif sql_upper.startswith("INSERT"):
        if "INTO" in sql_upper:
            parsed = pr.parse_insert(sql_command)
        elif "COLUMNS" in sql_upper:
            parsed = pr.parse_insert_col(sql_command)
    
    elif sql_upper.startswith("ADD COLUMNS"):
        parsed = pr.parse_add_column(sql_command)
    
    elif sql_upper.startswith("UPDATE"):
        if "TYPE" in sql_upper:
            parsed = pr.parse_upd_col(sql_command)
        else:
            parsed = pr.parse_update(sql_command)
    
    elif sql_upper.startswith("DROP"):
        parsed = pr.parse_drop(sql_command)
    
    elif sql_upper.startswith("SHOW"):
        parsed = pr.parse_show(sql_command)
    
    elif sql_upper.startswith("SELECT"):
        if "DISTINCT" in sql_upper:
            parsed = pr.parse_distinct_col(sql_command)
        elif "GROUP BY" in sql_upper:
            parsed = pr.parse_group_by(sql_command)
        elif ("ASC" in sql_upper or "DESC" in sql_upper):
            parsed = pr.parse_order_by_full(sql_command)
        elif "ORDER BY" in sql_upper:
            parsed = pr.parse_order_by_withcol(sql_command)
        elif "LIMIT" in sql_upper:
            parsed = pr.parse_limit(sql_command)
        elif "WHERE" in sql_upper:
            parsed = pr.parse_get(sql_command)
        else:
            parsed = pr.parse_select(sql_command)
    
    elif sql_upper.startswith("DELETE"):
        if "COLUMNS" in sql_upper:
            parsed = pr.parse_delete_allcol(sql_command)
        elif "ROWS" in sql_upper:
            parsed = pr.parse_delete_allrows(sql_command)
        elif "WHERE" in sql_upper:
            parsed = pr.parse_deleterows(sql_command)
    
    return parsed


def run_sql(sql_command):
    """Execute SQL without user context (for CLI)"""
    parsed = parse_sql(sql_command)
    
    if parsed is None:
        return None, "Invalid Syntax"
    
    result = execute_command(tm, parsed)
    cmd_type = parsed.get("type", "Invalid Syntax")
    
    return result, cmd_type


# ✅ NEW: User-specific execution
def run_sql_for_user(sql_command, user_id):
    """Execute SQL for specific user"""
    # Create user-specific table manager
    user_tm = TableManager(db_path=f"./Data/{user_id}", pickle_path=f"./Pickles/{user_id}",user_id=user_id)
    
    parsed = parse_sql(sql_command)
    
    if parsed is None:
        error_msg = "Invalid SQL syntax"
        print(error_msg)
        return {"error": error_msg}, "PARSE_ERROR"
    try:
        result = execute_command(user_tm, parsed)
        cmd_type = parsed.get("type", "UNKNOWN")
        
        query_types = [
            "SELECT", "WHERE", "LIMIT", "ORDER", "FULL",
            "DISTINCT", "GROUP BY"
        ]
       
        if cmd_type in query_types and result is None:
            return [], cmd_type
        
        return result, cmd_type
        
    except Exception as e:
        error_msg = f"Execution error: {str(e)}"
        print(f"❌ {error_msg}")
        import traceback
        traceback.print_exc()
        return {"error": error_msg}, "ERROR"
   

def main():
    print("=" * 60)
    print("🔥 LiteMySQL - Ek Lightweight SQL Database")
    print("=" * 60)
    print("\n📖 Commands:")
    print("  - CREATE TABLE tablename (col1 TYPE, col2 TYPE)")
    print("  - INSERT INTO tablename VALUES (val1, val2)")
    print("  - SELECT * FROM tablename WHERE Condition")
    print("  - SELECT * FROM tablename")
    print("  - DROP tablename")
    print("  - exit (program band karne ke liye)")
    print("\n" + "=" * 60 + "\n")
    
    while True:
        try:
            sql = input("litesql> ").strip()

            if not sql:
                continue

            if sql.lower() == "exit":
                print("litesql close 👋")
                break
            
            result, cmd_type = run_sql(sql)

        except KeyboardInterrupt:
            print("\n👋 litesql close (Ctrl+C)")
            break
        except Exception as e:
            print(f"error: {e}")


if __name__ == "__main__":
    main()
