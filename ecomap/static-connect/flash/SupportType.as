class SupportType{

    private var name:String;
    private var xPos:Number;
    private var yPos:Number;
    private var stationary:Boolean;
    private var depth:Number;
    private var support_mc:MovieClip;
    private var target_mc:MovieClip;

    private var constWidth:Number = 11;
    private var constHeight:Number = 13;


    public function SupportType(theDepth:Number, theTarget:MovieClip, theName:String, x:Number, y:Number, isStationary:Boolean){
    
        depth = theDepth;
        target_mc = theTarget;
        name = theName;
        stationary = isStationary;

        // Create the mc based on the name (MUST BE UNIQUE)
        support_mc = target_mc.createEmptyMovieClip(theName + "_mc",theDepth);
        support_mc.parent = this;

        // Letter representation for the support type
        support_mc.createTextField("name_txt",1,1,-2,10,14);
        var myStyle:TextFormat = new TextFormat("Tahoma",10);
        support_mc.name_txt.setNewTextFormat(myStyle);
        support_mc.name_txt.text = name.charAt(0).toUpperCase();


        support_mc.lineStyle(1,0xAAAAAA);
        support_mc.moveTo(0,0);
        support_mc.beginFill(0xCCCCCC);
        support_mc.lineTo(constWidth,0);
        support_mc.lineTo(constWidth,constHeight);
        support_mc.lineTo(0,constHeight);
        support_mc.lineTo(0,0);
        support_mc.endFill();

        setPosition(x,y);

        support_mc.onRelease = function(){
            this.stopDrag();

            // It was the root (toolbox) element so let it be added to any person
            if (this.parent.target_mc._name == ""){
                                
                if (this._droptarget.indexOf("container_mc") != -1){

                    // reference to the person it got dropped on
                    var thePerson:MovieClip = eval(this._droptarget.substr(0,this._droptarget.lastIndexOf("/")));
                    
                    // ADD IT TO THE PERSON (pass the constructor params needed)
                    thePerson.parent.addSupportType(this.parent.getName());
                    
                }
                // snap back the draggable toolbox element to the toolbox area
                this.parent.setPosition(this.oldX,this.oldY);

            // It was attached to a person already, so it's not a toolbox element
            }else{

                var currentParent:String = this._parent._name.substr(this._parent._name.indexOf("container_mc"));

                // You dragged it off and back onto the Person it was on before so snap it back into place
                if (this._droptarget.indexOf(currentParent) != -1){
                    this.parent.setPosition(this.oldX,this.oldY);

                // You dragged it off the Person it was on, so make it poof away
                }else{
                    this._parent.parent.removeSupportType(this.parent.getName());
                    this.removeMovieClip();
                }
            }

        }

        support_mc.onPress = function(){
            // if it's not stationary, start dragging it
            if (!isStationary){
                this.oldX = this._x;
                this.oldY = this._y;
                this.startDrag(false);
            }
        }

    
    }

    public function getInfo(){
        var info = support_mc._name;
        info += " " + name;
        info += " " + depth;
        return info;
    }


    public function getName(){
        return name;
    }

    public function setDepth(theDepth:Number){
        depth = theDepth;
        support_mc.swapDepths(depth);
    }


    public function setPosition(x:Number, y:Number){
        xPos = x;
        yPos = y;
        support_mc._x = xPos;
        support_mc._y = yPos;
    }
    
    
}