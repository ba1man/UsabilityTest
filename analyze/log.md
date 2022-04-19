## How tools print things in their logs

### ENRE-java

ENRE-java does not produce error message.

### ENRE-cpp

ENRE-cpp does not produce error message.

### ENRE-python

ENRE-python only produce warning message.

> ENRE-python does not produce error message on project `python-1-youtube-dl` while Understand does.

#### Warnings

```text
the module youtube-dl\youtube_dl\aes.py already imported by some analyzed module
```

### Depends

#### Errors

* **Java**

Depends lacks of error recovery methods.

```text
line 155:61 no viable alternative at input '@NonNull Iterable<@NonNull ?'

line 994:51 missing ':' at 'MaybeObserver'

line 221:8 mismatched input '.' expecting {'throws', '{'}

line 3866:0 extraneous input '}' expecting {<EOF>, 'abstract', 'class', 'enum', 'final', 'interface', 'private', 'protected', 'public', 'static', 'strictfp', ';', '@'}
```

* **C++**

Depends produce error on project `cpp-1-terminal` while Understand does not.

```text
warning: parse error using UInt64 = unsigned __int64;Syntax error in file: UsabilityTest\repo\terminal\dep\jsoncpp\json\json.h:347

parsing error

error

Syntax error in file: UsabilityTest\repo\terminal\src\renderer\dx\CustomTextLayout.cpp:132
```

#### StackOverflow

Depends crashes easily, by a stack overflow exception.

### SourceTrail


### Understand

#### Warnings

This is threw whenever a symbol can not be found, which usually represents a third-party library.

```text
Warning: Missing package org.junit.jupiter.api.Assertions
  File: path/to/file
```

#### Errors

This is threw whenever encountering a syntax error or new syntax that Understand's parser can not interprete.

```text
Error: expected token '>' at token Objects
  File: UsabilityTest\repo\RxJava\src\main\java\io\reactivex\rxjava3\core\Completable.java Line: 156
```

```java
@CheckReturnValue
@NonNull
@SchedulerSupport(SchedulerSupport.NONE)
public static Completable amb(@NonNull Iterable<@NonNull ? extends CompletableSource> sources) {
    Objects.requireNonNull(sources, "sources is null");

    return RxJavaPlugins.onAssembly(new CompletableAmb(null, sources));
}
```

> This is weird, Understand also retrives symbols from Java lib, yet still complain about the wrong syntax.
> 
> ```text
> Error: expected token 'class' or 'interface' at token sealed
>   File: Program Files\Eclipse Adoptium\jdk-17.0.2.8-hotspot\lib\src.zip{java.base\java\lang\constant\ConstantDesc.java} Line: 78
> ```

#### Convenient summary

Thanks to understand's final summary, counting errors and warnings is extremely easy.

```text
Analyze Completed (Errors:14 Warnings:5314)
```
