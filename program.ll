; ModuleID = "my_compiler"
target triple = "unknown-unknown-unknown"
target datalayout = ""

define i32 @"main"()
{
entry:
  %"a" = alloca i32
  store i32 0, i32* %"a"
  %".3" = call i32 (i8*, ...) @"printf"(i8* bitcast ([4 x i8]* @".str4725515630691834611" to i8*), i8* bitcast ([20 x i8]* @".str4918782734983268285" to i8*))
  %".4" = call i32 @"fflush"(i8* null)
  %".5" = call i32 (i8*, ...) @"scanf"(i8* bitcast ([3 x i8]* @".str5030970306535922903" to i8*), i32* %"a")
  %"a.1" = load i32, i32* %"a"
  %"icmptmp" = icmp sgt i32 %"a.1", 10
  br i1 %"icmptmp", label %"then", label %"else"
then:
  %".7" = call i32 (i8*, ...) @"printf"(i8* bitcast ([4 x i8]* @".str4725515630691834611" to i8*), i8* bitcast ([27 x i8]* @".str7262352148376039936" to i8*))
  %".8" = call i32 @"fflush"(i8* null)
  br label %"merge"
else:
  %".10" = call i32 (i8*, ...) @"printf"(i8* bitcast ([4 x i8]* @".str4725515630691834611" to i8*), i8* bitcast ([25 x i8]* @".str5726306198114121776" to i8*))
  %".11" = call i32 @"fflush"(i8* null)
  br label %"merge"
merge:
  %"i" = alloca i32
  store i32 0, i32* %"i"
  br label %"loop_header"
loop_header:
  %"i.1" = load i32, i32* %"i"
  %"a.2" = load i32, i32* %"a"
  %"icmptmp.1" = icmp slt i32 %"i.1", %"a.2"
  br i1 %"icmptmp.1", label %"loop_body", label %"after_loop"
loop_body:
  %".16" = call i32 (i8*, ...) @"printf"(i8* bitcast ([4 x i8]* @".str4725515630691834611" to i8*), i8* bitcast ([3 x i8]* @".str184026520705037517" to i8*))
  %".17" = call i32 @"fflush"(i8* null)
  %"i.2" = load i32, i32* %"i"
  %"ioptmp" = add i32 %"i.2", 1
  store i32 %"ioptmp", i32* %"i"
  br label %"loop_header"
after_loop:
  %".20" = call i32 (i8*, ...) @"printf"(i8* bitcast ([4 x i8]* @".str4725515630691834611" to i8*), i8* bitcast ([19 x i8]* @".str1220705876898242704" to i8*))
  %".21" = call i32 @"fflush"(i8* null)
  ret i32 0
}

declare i32 @"printf"(i8* %".1", ...)

declare i32 @"fflush"(i8* %".1")

@".str4918782734983268285" = constant [20 x i8] c"Escribe un numero: \00"
@".str4725515630691834611" = constant [4 x i8] c"%s\0a\00"
declare i32 @"scanf"(i8* %".1", ...)

@".str5030970306535922903" = constant [3 x i8] c"%d\00"
@".str7262352148376039936" = constant [27 x i8] c"Tu numero es mayor que 10.\00"
@".str5726306198114121776" = constant [25 x i8] c"Tu numero es 10 o menos.\00"
@".str184026520705037517" = constant [3 x i8] c"je\00"
@".str1220705876898242704" = constant [19 x i8] c"Conteo finalizado.\00"