用python实现一个项目功能，函数形参是一个json数据，该json数据内容基本格式例子如下：

​	{

​			"map":[

​					{"n":2,"param1":"string1data1","param2":"string1data2","button":"ctr1"}，

​					{"n":1,"param1":"string2data1","button":"ctr2"}，

​				{"n":3,"param1":"string3data1","param2":"string3data2","param3":"string3data3","button":"ctr3"}

​			]

​	}

对该json数据中的解释及功能说明：

1.map里的做为数组对象，上图为该map数组有3组对象，传输时map可以更多，该功能需要识别map有多少组对象赋值到map_len。同时检查各个对象内的数据字段是否符合协议格式,当字段'n'为N时,则该对象就必须要有字段'param1'到'paramN',同时'param1'到'paramN'的数据类型是string类型。各个对象的最后一个字段都有一个'button'且为string类型。符合上述描述则认为数据合法,如果不合法则弹出对话框报错并退出。创建一个空字典line_edit_map

2.创建一个QGridLayout网络布局，网络布局的摆放在窗体中间，宽度为80 *  map各个对象里的字段n的最大值，长度为40 * map_len。用for循环i<map_len依次遍历各个对象的内容，先创建一个列表line_edit_list_i,遍历操作为将获取对象的字段'n'的值,再次for循环j去遍历'param1'到'param' + str(j+1) 的值,每个param的遍历操作为对QGridLayout网络布局的第i行且第j*2列设置一个Qlabel标签,该标签文本设置为对应的'param' +str(j+1)字段的值。第i行第j*2+1设置一个QLineEdit,并将该QLineEdit对象添加到line_edit_list_i列表内。同时对button设置在最后一列。并在line_edit_map字典里添加一个元素，该元素键为button的显示文本，值为line_edit_list_i对象。

3.对数组内的各个对象的button按键做连接绑定一个预设的函数callback，该callback函数的实现是将

建立一个QGridLayout网络，

