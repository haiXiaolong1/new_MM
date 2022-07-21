$(document).ready(function() {
    $('#example').dataTable({
        "lengthMenu": [10, 25, 50, 75, 100],
        "language": {
            "processing": "正在加载中......",
            "lengthMenu": "每页显示 _MENU_ 条记录",
            "zeroRecords": "对不起，查询不到相关数据！",
            "emptyTable": "表中无数据存在！",
            "info": "当前显示 _START_ 到 _END_ 条，共 _TOTAL_ 条记录",
            "infoFiltered": "数据表中共为 _MAX_ 条记录",
            "search": "搜索",
            "paginate": {
                "first": "首页",
                "previous": "上一页",
                "next": "下一页",
                "last": "末页"
            }
        } //多语言配置
    });
});