COMPILER = g++
LIBS =
DEBUG_LIBS =
INCLUDES =
#-I/Library/Frameworks/SDL.framework/Headers/ -I../\!common/\!include/
RESULT = dis

default:
	@echo "Making: $(RESULT)"
	mkdir -p Release
	$(COMPILER) $(INCLUDES) -c *.cpp $(ADDITIONAL_CPP)
	mv *.o ./Release
	$(COMPILER) -o ./Release/$(RESULT) $(LIBS) ./Release/*.o

debug:
	mkdir -p Debug
	$(COMPILER) -g -rdynamic $(INCLUDES) -c *.cpp $(ADDITIONAL_CPP)
	mv *.o ./Debug
	$(COMPILER) -g -rdynamic -o ./Debug/$(RESULT) $(DEBUG_LIBS) ./Debug/*.o

run:
	./Release/$(RESULT)

clean:
	rm -f ./Release/$(RESULT) ./Debug/$(RESULT) ./Debug/*.o ./Release/*.o *.core core *~
