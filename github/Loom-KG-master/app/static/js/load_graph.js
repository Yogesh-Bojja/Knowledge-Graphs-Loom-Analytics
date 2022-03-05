(function scopeWrapper($) {

    var LabelList = new Array();
    var RelationList = new Array();

    var relation_info;
    var node_info;
    var dataset = new vis.DataSet();

    var removeRelationshipID = "";
    var removeNodeID = "";

    var checkboxes;

    var stack = new Array()

    //HTML Elements

    const drop = document.getElementById("drop")
    const check = document.getElementById("check-all")

    const dropDown = document.getElementById("nodeFilterSelect");
    const checkBox = document.getElementById("relationFilterSelect");
    const ToolOptions = document.getElementById("colorselector");

    const contextmenu = document.getElementById("context-menu");
    const contextMenuRelationship = document.getElementById("context-menu-relationship");

    const pathClick = document.getElementById("pathClick");

    const mergeNode1 = document.getElementById("node1merge");
    const mergeNode2 = document.getElementById("node2merge");

    const addRelationshipClick = document.getElementById("addRelationshipClick");
    const mergeClick = document.getElementById("mergeClick");

    const createNodeClick = document.getElementById("createNodeClick");
    const nodeRenameClick = document.getElementById("nodeRenameClick");


    $(function onDocReady() {
        graphInit();
    });

    function graphInit() {
        $.post('/graph/init_graph', {},
                function (data, status) {
                    localStorage.setItem('dataset', JSON.stringify(data));
                    initializeDataset(data)
                    drawGraph(dataset)
                    set()
                })
            .fail((err) => {
                console.log(err);
                alert("Error in initialising graph. See console for more info");
            })
    };

    function drawGraph(data) {
        var container = document.getElementById("viz");

        var options = {
            groups: {
                Person: {
                    width: "10",
                    fontsize: "10",
                },
                File: {
                    shape: "image",
                    image: "/static/icons/document.svg",
                    color: "red",
                    length: "50",
                },
            },
            interaction: {
                hover: true
            },
            nodes: {
                shape: "dot",
                size: 15,
                font: {
                    size: 15,
                    align: "middle"
                },
                borderWidth: 2,
                shadow: true
            },
            edges: {
                width: 2,
                font: {
                    align: "middle",
                    size: 11,
                    color: "green",
                },
                arrows: {}
            }
        };

        const network = new vis.Network(container, data, options);

        network.on('dragEnd', (e) => {
            if (e.nodes && e.nodes.length) {
                network.storePositions()
            }
        })

        var outcomeNode = "";
        network.on("click", function (params) {


            outcomeNode = "";
            document.getElementById("showMore").classList.add("card-option")
            $('#info-outcome').empty()


            //maintain stack of node click
            if (stack.length < 2) {
                stack.push(this.getNodeAt(params.pointer.DOM))
            } else {
                stack.splice(0, 1)
                this.getNodeAt(params.pointer.DOM)
            }
            if (ToolOptions.options[ToolOptions.selectedIndex].value == "relationship") {
                $("#node1").val(stack[0]);
                $("#node2").val(stack[1]);
                
            }
            if (ToolOptions.options[ToolOptions.selectedIndex].value == "path") {
                $("#node2path").val(stack[0]);
                $("#node2path").val(stack[1]);
            }

    
            if (ToolOptions.options[ToolOptions.selectedIndex].value == "path") {
                $("#node1short").val(stack[0]);
                $("#node2short").val(stack[1]);
            }

            if (ToolOptions.options[ToolOptions.selectedIndex].value == "span") {
                $("#nodeSpan").val(this.getNodeAt(params.pointer.DOM));
            }

            if (ToolOptions.options[ToolOptions.selectedIndex].value == "nodeProperty") {
                $("#nodePropertyID").val(this.getNodeAt(params.pointer.DOM));
            }

            if (ToolOptions.options[ToolOptions.selectedIndex].value == "merge") {
               
                $("#node1merge").val(stack[0]);
                $("#node2merge").val(stack[1]);
    
                var node1 = mergeNode1.value;
                var node2 = mergeNode2.value;

                dataset.nodes.forEach(node => {
                    if (node.id == node1) {
                        var name = "";
                        var type = "";
                        name = String(node.label)
                        type = String(node.group)
                        var text = "";
                        text = text.concat("<b>Name : </b>" + String(name) + " <br>");
                        text = text.concat("<b>Type : </b>" + String(type) + " <br>");

                        $('#nodeDescription1').empty();
                        $('#nodeDescription1').append(text);

                    } else if (node.id == node2) {
                        var name = "";
                        var type = "";
                        name = String(node.label)
                        type = String(node.group)
                        var text = "";
                        text = text.concat("<b>Name : </b>" + String(name) + " <br>");
                        text = text.concat("<b>Type : </b>" + String(type) + " <br>");

                        $('#nodeDescription2').empty();
                        $('#nodeDescription2').append(text);
                    }
                })
            }

            if (ToolOptions.options[ToolOptions.selectedIndex].value == "renameNode") {
                $("#nodeRename").val(this.getNodeAt(params.pointer.DOM))
                dataset.nodes.forEach(node => {
                    if (node.id == this.getNodeAt(params.pointer.DOM)) {
                        $("#nodeRenameCurrent").val(node.label)
                    }
                });
            }

            //Info card
            if (String(this.getNodeAt(params.pointer.DOM)) == "undefined") {
                $('#info-card').empty();
                $('#cardTitle').empty();
                $('#cardSubTitle').empty();

                $("#nodeRenameCurrent").val("");

                outcomeNode = "";

                document.getElementById("showMore").classList.add("card-option")
            } else {
                $(this).addClass('description');

                var data = JSON.parse(localStorage.getItem('dataset'));
                infoCard(data, this.getNodeAt(params.pointer.DOM))
            }
        });

        network.on("doubleClick", function (params) {
            var data = JSON.parse(localStorage.getItem('dataset'));

            if (String(this.getNodeAt(params.pointer.DOM)) != "undefined") {

                var idList = new Array();
                idList.push(this.getNodeAt(params.pointer.DOM))

                idfilter(data, idList)
                drawGraph({
                    nodes: node_info,
                    edges: relation_info
                })
            }
        });

        network.on("oncontext", function (params) {
            if (String(this.getNodeAt(params.pointer.DOM)) != "undefined") {

                event.preventDefault();
                var contextElement = document.getElementById("context-menu");
                contextElement.style.top = event.offsetY + 90 + "px";
                contextElement.style.left = event.offsetX + "px";
                contextElement.classList.add("active");
                removeNodeID = this.getNodeAt(params.pointer.DOM)
            } else if (String(this.getEdgeAt(params.pointer.DOM)) != "undefined") {

                event.preventDefault();
                var contextMenuRelationship = document.getElementById("context-menu-relationship");
                contextMenuRelationship.style.top = event.offsetY + 90 + "px";
                contextMenuRelationship.style.left = event.offsetX + "px";
                contextMenuRelationship.classList.add("active");
                removeRelationshipID = this.getEdgeAt(params.pointer.DOM)
            }
        });
    };

    contextmenu.addEventListener("click", (e) => {
        removeNode(removeNodeID)
    })

    contextMenuRelationship.addEventListener("click", (e) => {
        removeRelationship(removeRelationshipID)
    })

    //Initialize Raw Dataset
    function initializeDataset(graphInfo) {
        node_info = graphInfo.nodes
            .filter((node) => node.labels[0] != "Facts")
            .map((node) => {
                if (!LabelList.includes(node.labels[0])) {
                    LabelList.push(node.labels[0])
                }
                return {
                    id: node.id,
                    label: node.labels[0] == "File" ? node.properties.citation : node.properties.name,
                    group: node.labels[0]
                }
            });

        relation_info = graphInfo.relations
            .map((relation) => {
                if (!RelationList.includes(relation.type)) {
                    RelationList.push(relation.type)
                }
                return {
                    id: relation.id,
                    from: relation.node_ids[0],
                    to: relation.node_ids[1],
                    label: relation.type
                }
            })

        localStorage.setItem('nodes', JSON.stringify(node_info));
        localStorage.setItem('edges', JSON.stringify(relation_info));

        dataset = {
            nodes: node_info,
            edges: relation_info,
        };

        localStorage.setItem('finalData', JSON.stringify(dataset));

        return dataset;
    };

    //Set Dynamic Variables

    function set() {
        $('#nodeFilterSelect').empty();
        $('#NodeType').empty();
        $('#nodeFilterSelect').append($('<option></option>').val("All").html("All"));
        $.each(LabelList, function (i, p) {
            $('#nodeFilterSelect').append($('<option></option>').val(p).html(p));
            $('#NodeType').append($('<option></option>').val(p).html(p));
        });

        $('#relationFilterSelect').empty();
        $('#relationFilterSelect').append($('<a href="#" data-toggle="check-all" class="dropdown-option" id="check-all">  Check All </a>').val("check-all").html("check-all"));
        $('#relationFilterSelect').append($('<a href="#" data-toggle="check-all" class="dropdown-option" id="uncheck-all">  Uncheck All </a>').val("uncheck-all").html("uncheck-all"));

        $.each(RelationList, function (i, p) {
            var string = '<label class="dropdown-option"><input type="checkbox" class="auto-width" name="dropdown-group" value="' + p + '"id="' + p + '"checked />' + p + '</label>'
            $('#relationFilterSelect').append(string).val(p);
        });
        checkboxes = document.querySelectorAll("input[type=checkbox]");

        $('#check-all').click(e => {
            $.each(RelationList, function (i, p) {
                document.getElementById(p).checked = true;
            });
        })

        $('#uncheck-all').click(e => {
            $.each(RelationList, function (i, p) {
                document.getElementById(p).checked = false;
            });
        })

        let enabledSettings = []

        checkboxes.forEach(function (checkbox) {
            checkbox.addEventListener('change', function () {
                enabledSettings = Array.from(checkboxes)
                    .filter(i => i.checked)
                    .map(i => i.value)

                var data = JSON.parse(localStorage.getItem('dataset'));
                relationFilter(data, enabledSettings)
                drawGraph({
                    nodes: node_info,
                    edges: relation_info
                })
            })
        });
    };

    //Filter Functions
    function filter(data, filter) {
        node_info = data.nodes
            .filter((node) => node.labels[0] == filter)
            .map((node) => {
                return {
                    id: node.id,
                    label: node.labels[0] == "File" ? node.properties.citation : node.properties.name,
                    group: node.labels[0]
                }
            });
        return node_info
    };

    function idfilter(data, id) {
        var nodeList = new Array();

        id.forEach(ids => {
            data.relations.forEach(relation => {
                if (relation.node_ids[0] == ids | relation.node_ids[1] == id) {
                    if (!nodeList.includes(relation.node_ids[0])) {
                        nodeList.push(relation.node_ids[0])
                    }

                    if (!nodeList.includes(relation.node_ids[1])) {
                        nodeList.push(relation.node_ids[1])
                    }
                }
            })
        })

        node_info = data.nodes
            .filter((node) => nodeList.includes(node.id))
            .map((node) => {
                return {
                    id: node.id,
                    label: node.labels[0] == "File" ? node.properties.citation : node.properties.name,
                    group: node.labels[0]
                }
            });


        return node_info
    };

    function relationFilter(data, type) {
        var nodeList = new Array();

        type.forEach(element => {
            data.relations.forEach(relation => {
                if (relation.type == element) {
                    if (!nodeList.includes(relation.node_ids[0])) {
                        nodeList.push(relation.node_ids[0])
                    }

                    if (!nodeList.includes(relation.node_ids[1])) {
                        nodeList.push(relation.node_ids[1])
                    }
                }
            })
        })

        node_info = data.nodes
            .filter((node) => nodeList.includes(node.id))
            .map((node) => {
                return {
                    id: node.id,
                    label: node.labels[0] == "File" ? node.properties.citation : node.properties.name,
                    group: node.labels[0]
                }
            });


        return node_info
    };

    //End Filter Functions

    function infoCard(data, id) {
        var info = "";
        var name = "";
        var type = "";

        data.nodes.forEach(node => {
            if (node.id == id) {
                $('#info-outcome').empty();

                name = node.labels[0] == "File" ? String(node.properties.citation) : String(node.properties.name)
                type = String(node.labels[0])


                info = info.concat("<b>ID : </b>" + String(node.id) + " <br>");
                
                if (node.labels[0] == "File") {
                    name = String(node.properties.citation_full)
                    info = info.concat("<b>Court Date : </b>" + String(node.properties.court_date) + " <br>");
                    info = info.concat("<b>Court Location : </b>" + String(node.properties.court_location) + " <br>");

                    document.getElementById("showMore").classList.remove("card-option")
                    outcomeNode = id;
                }
            }
        })

        $('#info-card').empty();
        $('#info-card').append(info);
        $('#cardTitle').empty();
        $('#cardTitle').append(name);
        $('#cardSubTitle').empty();
        $('#cardSubTitle').append(type);
    };

    // Event Listners

    window.addEventListener("click", function (event) {
        contextmenu.classList.remove("active");
        contextMenuRelationship.classList.remove("active");
    });

    dropDown.addEventListener("change", (e) => {
        filterValue = e.target.value;
        var data = JSON.parse(localStorage.getItem('dataset'));
        if (filterValue != "All") {
            filter(data, filterValue)
            drawGraph({
                nodes: node_info,
                edges: relation_info
            })
        } else {
            drawGraph(dataset)
        }
    });

    check.addEventListener("click", (e) => {
        checkboxes.forEach(checkbox => {
            checkbox.checked = true;
        })
        drawGraph(dataset)
    });

    pathClick.addEventListener("click", e => {
        shortestPath()
    })

    ToolOptions.addEventListener("change", (e) => {
        if (e.target.value == "relationship") {
            addRelationship = true
            stack = [];
            $("#node1").val("");
            $("#node2").val("");

        } else if (e.target.value == "path") {
            stack = [];
            $("#node1span").val("");
            $("#node1span").val("");

        } else if (e.target.value == "merge") {

            stack = [];
            $("#node1merge").val("");
            $("#node2merge").val("");
        } else {
            return
        }
    });

    addRelationshipClick.addEventListener("click", (e) => {
        createRelationship()
    });

    mergeClick.addEventListener("click", (e) => {
        mergeNode()
    })

    createNodeClick.addEventListener("click", (e) => {
        createNode()
    });

    nodeRenameClick.addEventListener("click", event => {
        renameNode()
    })

    const showMore = document.getElementById("showMore")
    showMore.addEventListener("click", e => {
        getOutcome(outcomeNode)
    })

    $("#Refresh").click(function () {
        graphInit()
    });

    //Graph Manipulation Functions

    function getOutcome(nodeID) {
        var url = '/graph/get_file_details'

        $.post(url, {
                    node_id: nodeID
                },
                function (data, status) {

                    Object.keys(data.result[0].node).forEach(function (key) {
                        var value ="";
                        if(key=="for_citation" | key=="name")
                        {
                            value ="<b>" + data.result[0].node[key] +"\n </b>";
    
                        }else {
                            value = "<br>" + data.result[0].node[key];
                        }
    
                        $('#info-outcome').append(value)
    
                    });
                    $('#info-outcome').append('<br>')
    
                    Object.keys(data.result[1].node).forEach(function (key) {
                        var value ="";
                        if(key=="for_citation" | key=="name")
                        {
                            value ="<b>" + data.result[1].node[key] +"\n</b>";
    
                        }else {
                            value = "<br>" + data.result[1].node[key];
                        }
                
    
                        $('#info-outcome').append(value)
    
                    })

                })
            .fail((err) => {
                console.log(err)
            })
    }

    function createNode() {
        let name = "";
        let nodeType = "";

        name = document.getElementById("NodeNameTextBox").value
        nodeType = document.getElementById("NodeType").value;

        if (name != "") {
            var answer = window.confirm("Do you wish to proceed adding node [" + name + "] ?");
            if (answer) {
                var url = '/graph/create_node'

                $.post(url, {
                            name: name,
                            node_type: nodeType
                        },
                        function (data, status) {
                            graphInit()
                            document.getElementById("NodeNameTextBox").value = ""
                            alert("Add Node Operation Successful");

                        })
                    .fail((err) => {
                        alert("Add Node Operation Failed");
                        console.log(err)
                    })
            } else {
                alert("Add Node Operation Cancelled");
                return;
            }
        } else {
            alert("Please enter valid name");
        }
    };

    function removeNode(NodeID) {
        var removeNodeId = NodeID;

        if (removeNodeId != "undefined" && removeNodeId != "") {
            var answer = window.confirm("Do you wish to proceed removing node [" + removeNodeId + "] ?");
            if (answer) {

                var url = '/graph/remove_node'

                $.post(url, {
                            node_id: removeNodeId
                        },
                        function (data, status) {
                            graphInit();
                            removeNodeID = "";
                            alert("Delete Node Operation Successful");

                        })
                    .fail((err) => {
                        alert(err);
                    })
            } else {
                alert("Delete Node Operation Cancelled");
                return;
            }
        } else {
            alert("");
        }
    };

    function mergeNode() {
        let node1 = "";
        let node2 = "";

        node1 = mergeNode1.value;
        node2 = mergeNode2.value;

        if (node1 != "" && node2 != "") {
            node1type = dataset.nodes
                .filter((node) => node.id == node1)
                .map((node) => {
                    return {
                        type: node.group
                    }
                });

            node2type = dataset.nodes
                .filter((node) => node.id == node2)
                .map((node) => {
                    return {
                        type: node.group
                    }
                });

            if (node1type[0].type == node2type[0].type) {
                var url = '/graph/merge_nodes'
                $.post(url, {
                            node_id_1: node1,
                            node_id_2: node2,
                        },
                        function (data, status) {
                            graphInit()
                            alert("Merge Node Operation Successful");
                        })
                    .fail((err) => {
                        console.log(err)
                    })
            } else {
                alert("Please select nodes of same type")
                return;
            }

        } else {
            alert("Please select two nodes of same type")
            return
        }
    };

    function renameNode() {
        var NodeID = "";
        var newName = "";

        NodeID = document.getElementById("nodeRename").value;
        newName = document.getElementById("nodeRenameTextBox").value;

        if (NodeID != "" && newName != "") {
            var url = '/graph/rename_node'

            $.post(url, {
                        node_id: NodeID,
                        name: newName
                    },
                    function (data, status) {
                        graphInit()
                        alert("Rename Operation Successful");

                    })
                .fail((err) => {
                    alert(err);
                })
        } else {
            alert("Enter a valid node name")
        }
    }

    const nodePropertyClick = document.getElementById("nodePropertyClick")
    nodePropertyClick.addEventListener("click", e => {
        setNodeProperty()
    });

    function setNodeProperty() {
        var nodeID = document.getElementById("nodePropertyID").value;
        var nodePropertyName = document.getElementById("nodePropertyName").value;
        var nodePropertyValue = document.getElementById("nodePropertyValue").value;

        if (nodePropertyName != "" && nodePropertyValue != "") {
            var url = '/graph/set_node_property'
            $.post(url, {
                        node_id: nodeID,
                        key: nodePropertyName,
                        value: nodePropertyValue
                    },
                    function (data, status) {
                        alert("Node property set successfully")
                    })
                .fail((err) => {
                    alert(err);
                })

        } else {
            alert("Please enter valid name and value")
        }
    }

    function createRelationship() {
        let node1 = "";
        let node2 = "";
        let relationshipType = "";

        node1 = document.getElementById("node1").value;
        node2 = document.getElementById("node2").value;
        relationshipType = document.getElementById("relationshipType").value;

        if (node1 != "" && node2 != "" && relationshipType != "") {
            var answer = window.confirm("Do you wish to proceed realtionship [" + relationshipType + "] between node ids [" + node1 + "] & [" + node2 + "] ?");
            if (answer) {

                var url = '/graph/create_relationship'
                $.post(url, {
                            node_id_1: node1,
                            node_id_2: node2,
                            relation_type: relationshipType
                        },
                        function (data, status) {
                            graphInit()
                            alert("Add Relationship Operation Successful");
                        })
                    .fail((err) => {
                        console.log(err)
                    })
            } else {
                alert("Add Relationship Operation Cancelled");
            }
        } else {
            alert("Please enter valid details");
        }
    };

    function removeRelationship(relID) {
        var removeRelationID = relID;

        if (removeRelationID != "") {
            var answer = false;
            var answer = window.confirm("Do you wish to proceed removing relation ?");
            if (answer) {
                var url = '/graph/remove_relationship'
                $.post(url, {
                            relation_id: removeRelationID
                        },
                        function (data, status) {
                            graphInit()
                            removeRelationshipID = "";
                            alert("Delete Relation Operation Successful");

                        })
                    .fail((err) => {
                        alert(err);
                    })
            } else {
                alert("Delete Relation Operation Cancelled");
                return;
            }
        } else {
            alert("");
        }
    };

    const spanClick = document.getElementById("spanClick")

    spanClick.addEventListener("click", e => {
        spanningTree()
    });

    function spanningTree() {
        let node = "";
        node = document.getElementById("nodeSpan").value;

        var url = '/graph/spanning_tree'
        $.post(url, {
                    node_id: node
                },
                function (data, status) {
                    node_info = data.nodes
                        .map((node) => {
                            return {
                                id: node.id,
                                label: node.labels[0] == "File" ? node.properties.citation : node.properties.name,
                                group: node.labels[0]
                            }
                        });

                    drawGraph({
                        nodes: node_info,
                        edges: relation_info
                    })
                })
            .fail((err) => {
                alert(err);
            })
    }

    function shortestPath() {
        let node1 = "";
        let node2 = "";
        node1 = document.getElementById("node1span").value;
        node2 = document.getElementById("node2span").value;

        if (node1 != "" && node2 != "") {
            if (node1 == node2) {
                alert("Please select two different nodes")
                return
            }

            var url = '/graph/get_shortest_path'
            $.post(url, {
                        node_id_1: node1,
                        node_id_2: node2,

                    },
                    function (data, status) {
                        var idList = Array()
                        var relList = new Array();

                        data.relations.forEach((e) => {
                            if (!idList.includes(e.node_ids[0])) {
                                idList.push(e.node_ids[0])
                            }

                            if (!idList.includes(e.node_ids[1])) {
                                idList.push(e.node_ids[1])
                            }

                            if (!relList.includes(e.id)) {
                                relList.push(e.id)
                            }
                        })

                        var data = JSON.parse(localStorage.getItem('dataset'));

                        relation_info = data.relations
                            .filter((relation) => relList.includes(relation.id))
                            .map((relation) => {
                                return {
                                    from: relation.node_ids[0],
                                    to: relation.node_ids[1],
                                    label: relation.type
                                }
                            });

                        node_info = data.nodes
                            .filter((node) => idList.includes(node.id))
                            .map((node) => {
                                return {
                                    id: node.id,
                                    label: node.labels[0] == "File" ? node.properties.citation : node.properties.name,
                                    group: node.labels[0]
                                }
                            });


                        drawGraph({
                            nodes: node_info,
                            edges: relation_info
                        });
                    })
                .fail((err) => {
                    console.log(err)
                })

        } else {
            alert("Please select at least two nodes")
        }
    };
}(jQuery));

(function ($) {
    var CheckboxDropdown = function (el) {
        var _this = this;
        this.isOpen = false;
        this.areAllChecked = false;
        this.$el = $(el);
        this.$label = this.$el.find('.dropdown-label');
        this.$checkAll = this.$el.find('[data-toggle="check-all"]').first();
        this.$inputs = this.$el.find('[type="checkbox"]');

        this.onCheckBox();

        this.$label.on('click', function (e) {
            e.preventDefault();
            _this.toggleOpen();
        });

        this.$checkAll.on('click', function (e) {
            e.preventDefault();
            _this.onCheckAll();
        });

        this.$inputs.on('change', function (e) {
            _this.onCheckBox();
        });
    };

    CheckboxDropdown.prototype.onCheckBox = function () {
        this.updateStatus();
    };

    CheckboxDropdown.prototype.updateStatus = function () {
        var checked = this.$el.find(':checked');

        this.areAllChecked = false;
        this.$checkAll.html('Check All');

        if (checked.length <= 0) {
            this.$label.html('Select Options');
        } else if (checked.length === 1) {
            this.$label.html(checked.parent('label').text());
        } else if (checked.length === this.$inputs.length) {
            this.$label.html('All Selected');
            this.areAllChecked = true;
            this.$checkAll.html('Uncheck All');
        } else {
            this.$label.html(checked.length + ' Selected');
        }
    };

    CheckboxDropdown.prototype.onCheckAll = function (checkAll) {
        if (!this.areAllChecked || checkAll) {
            this.areAllChecked = true;
            this.$checkAll.html('Uncheck All');
            this.$inputs.prop('checked', true);
        } else {
            this.areAllChecked = false;
            this.$checkAll.html('Check All');
            this.$inputs.prop('checked', false);
        }

        this.updateStatus();
    };

    CheckboxDropdown.prototype.toggleOpen = function (forceOpen) {
        var _this = this;

        if (!this.isOpen || forceOpen) {
            this.isOpen = true;
            this.$el.addClass('on');
            $(document).on('click', function (e) {
                if (!$(e.target).closest('[data-control]').length) {
                    _this.toggleOpen();
                }
            });
        } else {
            this.isOpen = false;
            this.$el.removeClass('on');
            $(document).off('click');
        }
    };

    var checkboxesDropdowns = document.querySelectorAll('[data-control="checkbox-dropdown"]');
    for (var i = 0, length = checkboxesDropdowns.length; i < length; i++) {
        new CheckboxDropdown(checkboxesDropdowns[i]);
    }

    $(function () {
        $('#colorselector').change(function () {
            $('.colors').hide();
            $('#' + $(this).val()).show();
        });
    });
})(jQuery);