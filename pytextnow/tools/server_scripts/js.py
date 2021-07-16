

def dom_query(q_type, value):
    """
    Buid a piece of JS that gets an element using the data
    that we were given
    """
    if "q" in q_type:
        return "document.querySelectorAll('%s');"
    return "document.getElementBy"+q_type.split("_").title()+"("+value+");"

def event_listener(js_query, js_event, handler):
    return """
    var elems = %s;
    for (var i=0; i++; i < elems.length){
        elem.addEventListener('%s', %s(function(e){
            // Pass the element to the handler
            %s(e);
        }));
    }
    """ % (
        js_query, js_event,
        handler
    )

def send_notif_func(url, data):
    """
    NOTE: All we need to do is alert the main thread that there
    is a new thing that needs to be gotten from the api and saved.

    Build an AJAX script to send some information to the server
    """
    return """
    function notifyServer(elem){
        $.ajax({
            url: "/%s/",
            data: %s,
            success : function(data){
                // Give some sort of feedback to show that the event
                // was fired and the server recieved the message
                console.log(data);
            } error : function(data){
                // Again, give feedback
                console.log(data);
            }
        });
    }
    """ % (url, data)

def inject_comms_script(
    dom_query, notify_script,
    binding_loop
):
    """
    Get it? Injecting the script :3

    Build the script that injects the JavaScript
    to communicate with the server.
    """
    return """
    //                        .--.          
//            ,-.------+-.|  ,-.     
//   ,--=======* )"("")===)===* )    
//   �        `-"---==-+-"|  `-"     
//   O                 '--'      JW  
//   V
    // Get elements
    %s;
    // Define notifyServer function
    %s
    // Get event bind loop
    %s
    """ % (
        dom_query,
        notify_script,
        binding_loop
    )