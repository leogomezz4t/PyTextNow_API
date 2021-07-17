from enum import IntEnum
import operator

class JavascriptSnippet:
    class Type(IntEnum):
        # Raw javascript code (inject as-is)
        Raw = 0
        # Not implemented
        Func = 1
        # Not implemented
        Assignment = 2

    class Order(IntEnum):
        # Sets the order things happen in.
        # If the order isn't important, use Order.Middle
        # so that other things that are more order-sensitive
        # can still happen before or after.
        Start = 1
        Early = 2
        Middle = 3
        Late = 4
        End = 5

        __ordering__ = [Start, Early, Middle, Late, End]

    # Actual storage for this snippet
    type = None
    order = None
    data = None

    def __init__(self, data, type=Type.Raw, order=Order.Middle):
        print("JS Snippet: type=%s order=%s data=`%s`" % (type.name, order.name, str(data)))
        self.type = type
        self.order = order
        self.data = data

    def to_string(self):
        if self.type == self.Type.Raw:
            return self.data
        else:
            raise ValueError("Invalid Type: '%s' (%i)" % (type.name, type.value))

class JavascriptGenerator:
    def combine_snippets(snippets, asSnippet=False, addScriptTags=False):
        snippets.sort(key=operator.attrgetter('order'))

        result = "\n"
        for snippet in snippets:
            result += snippet.to_string() + "\n"

        if addScriptTags:
            result = "<script>"+result+"</script>"

        if asSnippet:
            result = JavascriptSnippet(result)

        return result

    def event_handler(object, event, name=None):
        print("Event handler")

    def dom_query(q_type, value):
        """
        Buid a piece of JS that gets an element using the data
        that we were given
        """
        if "q" in q_type:
            return JavascriptSnippet("document.querySelectorAll('%s');" % value)
        return JavascriptSnippet("document.getElementBy"+q_type.split("_").title()+"("+value+");")

    def event_listener(js_query, js_event, handler):
        return JavascriptSnippet("""
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
        ))

    def send_notif_func(url, data):
        """
        NOTE: All we need to do is alert the main thread that there
        is a new thing that needs to be gotten from the api and saved.

        Build an AJAX script to send some information to the server
        """
        return JavascriptSnippet("""
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
        """ % (url, data))

    def inject_comms_script(dom_query, notify_script, binding_loop):
        """
        Get it? Injecting the script :3

        Build the script that injects the JavaScript
        to communicate with the server.
        """
        return JavascriptSnippet("""
//                        .--.
//            ,-.------+-.|  ,-.
//   ,--=======* )"("")===)===* )
//   |        `-"---==-+-"|  `-"
//   O                 '--'
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
        ))


if __name__ == "__main__":
    # Run tests
    dom_q = JavascriptGenerator.dom_query("q", "type.class#id")
    assert dom_q.data == "document.querySelectorAll('type.class#id');"

    snippet = JavascriptGenerator.combine_snippets([dom_q, dom_q], addScriptTags=True, asSnippet=True)
    assert snippet.data == """<script>
document.querySelectorAll('type.class#id');
document.querySelectorAll('type.class#id');
</script>"""
