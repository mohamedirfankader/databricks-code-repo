# Databricks notebook source
dbutils.widgets.removeAll()

# COMMAND ----------

# MAGIC %md
# MAGIC #We are going to learn usage of dbutils (DB Utilities...) + widgets (interesting dbutil)

# COMMAND ----------

# MAGIC %fs ls

# COMMAND ----------

# MAGIC %md
# MAGIC #####1. Display the list databricks utils
# MAGIC ######Below dbutils is the comprehensive one, out of which we are going to concentrate currently on notebook, widgets and fs for now

# COMMAND ----------

dbutils.help()
#Some of the important utils...
#fs, notebook, widgets, secrets (security management)

# COMMAND ----------

# MAGIC %md
# MAGIC #####2. Notebook's particular utils help

# COMMAND ----------

dbutils.fs.help()

# COMMAND ----------

# MAGIC %md
# MAGIC #####3. Widgets utils help

# COMMAND ----------

dbutils.widgets.help()
#4 Important widgets
#combobox, dropdown, text, multiselect

# COMMAND ----------

# MAGIC %md
# MAGIC #####4. Let's create all those widgets/plugins/components, attach to this notebook, capture the widget content and make use of it...

# COMMAND ----------

dbutils.widgets.removeAll()

# COMMAND ----------

# MAGIC %md
# MAGIC ######A. Text widget

# COMMAND ----------

#creating and attaching a widget (simple and important widget)
dbutils.widgets.text("aspirant_name","Thilaga","enter our aspirant name to wish")

# COMMAND ----------

#capture the widget input in a variable
name_of_aspirant=dbutils.widgets.get("aspirant_name")
#use that variable for some purpose
print(f"Congratulations!!! {name_of_aspirant}")

# COMMAND ----------

# MAGIC %md
# MAGIC ######B. Dropdown widget

# COMMAND ----------

dbutils.widgets.dropdown("aspirant_gender","Female",["Male","Female"])
gender=dbutils.widgets.get("aspirant_gender")
print(f"Gender of aspirant is {gender}")

# COMMAND ----------

# MAGIC %md
# MAGIC ######C. Combobox widget - Used to choose only one value from the dropdown by searching

# COMMAND ----------

dbutils.widgets.combobox("aspirant_country_combo","India",["India","USA","UK","Canada","Australia"])
country=dbutils.widgets.get("aspirant_country_combo")
print(f"Country of aspirant is {country}")

# COMMAND ----------

# MAGIC %md
# MAGIC ######D. Multiselect widget  - Used to choose multiple values from the dropdown by searching

# COMMAND ----------

dbutils.widgets.multiselect("aspirant_hobbies_multiselect","Dance",["Dance","Music","Sports","Reading","Writing"])
hobbies=dbutils.widgets.get("aspirant_hobbies_multiselect")
print(f"Hobbies of aspirant are {hobbies}",type(hobbies))
print("Top and Least hobbies ?", hobbies.split(",")[0],hobbies.split(",")[-1])

# COMMAND ----------

all_widgets=dbutils.widgets.getAll()
print(all_widgets)

# COMMAND ----------

# MAGIC %md
# MAGIC #####5. Dynamic SQL usecase to try on dropdown widget?
# MAGIC 1. Collect the list of tables present in the catalog/schema/tables
# MAGIC 2. substitute in the dropdown widgets
# MAGIC 3. allow user to choose the respective table and execute the query to return the total number of rows in that table chosen.<br>
# MAGIC 4. How you can explain this in the interview?
# MAGIC ..............................................................................................................
# MAGIC

# COMMAND ----------

# MAGIC %md
# MAGIC #####6. DBUtils FS Commands - For doing DBFS operations

# COMMAND ----------

dbutils.fs.help()
#cp(from: String, to: String, recurse: boolean = false): boolean -> Copies a file or directory, possibly across FileSystems
#head(file: String, maxBytes: int = 65536): String -> Returns up to the first 'maxBytes' bytes of the given file as a String encoded in UTF-8
#ls(dir: String): Seq -> Lists the contents of a directory
#mkdirs(dir: String): boolean -> Creates the given directory if it does not exist, also creating any necessary parent directories
#mv(from: String, to: String, recurse: boolean = false): boolean -> Moves a file or directory, possibly across FileSystems
#put(file: String, contents: String, overwrite: boolean = false): boolean -> Writes the given String out to a file, encoded in UTF-8
#rm(dir: String, recurse: boolean = false): boolean -> Removes a file or directory


# COMMAND ----------

dbutils.fs.mkdirs("dbfs:/Volumes/workspace/default/volumewe47_datalake/directory1")
data="hello team"
dbutils.fs.put("dbfs:/Volumes/workspace/default/volumewe47_datalake/directory1/sample.txt",data,True)
dbutils.fs.ls("dbfs:/Volumes/workspace/default/volumewe47_datalake/directory1")
print(dbutils.fs.head("dbfs:/Volumes/workspace/default/volumewe47_datalake/directory1/sample.txt",5))#Want to see the top 5 bytes of data
dbutils.fs.cp("dbfs:/Volumes/workspace/default/volumewe47_datalake/directory1/sample.txt","dbfs:/Volumes/workspace/default/volumewe47_datalake/directory1/sample.txt_copy2.csv")
dbutils.fs.mv("dbfs:/Volumes/workspace/default/volumewe47_datalake/directory1/sample.txt_copy2.csv","dbfs:/Volumes/workspace/default/volumewe47_datalake/directory1/sample.txt_moved.csv")
dbutils.fs.rm("dbfs:/Volumes/workspace/default/volumewe47_datalake/directory1/sample.txt")

# COMMAND ----------

# MAGIC %md
# MAGIC #####7. Calling a child notebook (example_child_notebook.ipynb) from this parent notebook with parameters
# MAGIC dbutils.widgets.text("param1", "default_value", "Your input parameter")
# MAGIC param_value = dbutils.widgets.get("param1")
# MAGIC print("printing the parameters",param_value)

# COMMAND ----------

# MAGIC %md
# MAGIC #####Imporantant interview question: Difference between run magic and dbutils command?
# MAGIC A. The %run magic command will run some other notebook inline in this current notebook itself, so we don't have write some other notebook code, rather we can just run it...<br>
# MAGIC B. The dbutils.notebook.run() command will trigger some other notebook in the respective notebook environment itself, and we can add additional parameters such as timeout seconds and custom parameters to the widgets we can pass...

# COMMAND ----------

# MAGIC %run "/Workspace/Users/infoblisstech@gmail.com/databricks-code-repo/databricks_workouts_2025_WE47/1_DATABRICKS_NOTEBOOK_FUNDAMENTALS/4_child_notebook"

# COMMAND ----------

return_status=dbutils.notebook.run("/Workspace/Users/infoblisstech@gmail.com/databricks-code-repo/databricks_workouts_2025_WE47/1_DATABRICKS_NOTEBOOK_FUNDAMENTALS/4_child_notebook",90,{"table_name":"cust"})
print("child notebook ",return_status)

# COMMAND ----------

#####Interview question...
fullname="inceptez technologies"
print(fullname)
fullname_lst=fullname.split(" ")
print(fullname_lst)
fname=fullname.split(" ")[0]
lname=fullname.split(" ")[-1]
print(fname,lname)
