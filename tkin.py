import tkinter as tk
import math_1 as m


root = tk.Tk()
tk.Label(root,text="Calculator").grid(row=0,column=0)
entry  = tk.Entry(root)
entry.grid(row=1,column=0)
tk.Button(root,text="+",command=lambda: entry.insert(tk.END,"+")).grid(row=2,column=0,padx=5, pady=5)
tk.Button(root,text="-",command=lambda: entry.insert(tk.END,"-")).grid(row=3,column=0,padx=5, pady=5)
tk.Button(root,text="*",command=lambda: entry.insert(tk.END,"*")).grid(row=4,column=0,padx=5, pady=5)
tk.Button(root,text="/",command=lambda: entry.insert(tk.END,"/")).grid(row=5,column=0,padx=5, pady=5)
tk.Button(root,text="1",command=lambda: entry.insert(tk.END,"1")).grid(row=2,column=1,padx=5, pady=5)
tk.Button(root,text="2",command=lambda: entry.insert(tk.END,"2")).grid(row=2,column=2,padx=5, pady=5)
tk.Button(root,text="3",command=lambda: entry.insert(tk.END,"3")).grid(row=2,column=3,padx=5, pady=5)
tk.Button(root,text="4",command=lambda: entry.insert(tk.END,"4")).grid(row=3,column=1,padx=5, pady=5)
tk.Button(root,text="5",command=lambda: entry.insert(tk.END,"5")).grid(row=3,column=2,padx=5, pady=5)
tk.Button(root,text="6",command=lambda: entry.insert(tk.END,"6")).grid(row=3,column=3,padx=5, pady=5)
tk.Button(root,text="7",command=lambda: entry.insert(tk.END,"7")).grid(row=4,column=1,padx=5, pady=5)
tk.Button(root,text="8",command=lambda: entry.insert(tk.END,"8")).grid(row=4,column=2,padx=5, pady=5)
tk.Button(root,text="9",command=lambda: entry.insert(tk.END,"9")).grid(row=4,column=3,padx=5, pady=5)
tk.Button(root,text="0",command=lambda: entry.insert(tk.END,"0")).grid(row=5,column=1,padx=5, pady=5)
tk.Button(root,text="c",command=lambda: entry.delete(0,tk.END)).grid(row=5,column=3,padx=5, pady=5)
def calculate():
    exp = entry.get()
    list = ["*","+","-","/","**","%"]
    for ele in list:
        if ele in exp:
            print(ele)
            x,y = exp.split(ele)
            x = float(x.strip())
            y = float(y.strip())
            try:
                match ele:
                    case "+":
                        op = m.add(x,y)
                    case "-":
                        op = m.sub(x,y)
                    case "*":
                        op = m.mul(x,y)
                    case "/":
                        op = m.div(x,y)
                    case "%":
                        op = m.mod(x,y)
                    case "**":
                        op = m.expo(x,y)
            except ZeroDivisionError:
                op = 0
            except Exception as e:
                exit()
     
            entry.delete(0, tk.END)
            entry.insert(tk.END, str(op))
                
tk.Button(root,text="=",command=calculate).grid(row=5,column=2,padx=5, pady=5)
tk.Button(root,text="Ex",command=lambda: exit()).grid(row=5,column=4,padx=5, pady=5)

root.mainloop()