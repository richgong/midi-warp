Option Explicit

On Error Resume Next

Dim Speaker 'Becomes the object that is used to speak.
Dim VoiceList, Voice 'Used in the loop to list the available voices
Dim Words 'Words to speak
Dim Speed 'Speed to speak, range is -10 (slow) to 10 (fast)

'Create the speaker object
Set Speaker = CreateObject("SAPI.SpVoice")

'Get the words to speak
Words = WScript.Arguments.Item(0)

If Err.Number = 9 Then 'No command line parameters entered, including words to speak.  Popup a usage dialog

 Words="Nothing to say!" & vbCrLf & vbcrlf & "Syntax:" & vbCrLf & "SPEAK ""hello world"" [slow|normal|fast|-10 to 10]"
 MsgBox Words

Else

 If Lcase(WScript.Arguments.Item(0)) = "list" Then 'list the voices available - most systems only have the default Microsoft Ana.

  For each Voice in Speaker.GetVoices
   VoiceList = VoiceList & Voice.GetDescription & vbcrlf
  Next

  MsgBox VoiceList

 Else 'speak the word or words in quotes specified as the first parameter

  Select Case LCASE(WScript.Arguments.Item(1)) 'If a second parameter is specified, it's the speed of the voice.  Talk slow or Talk fast.
   Case "slow"
    Speed = -5 'slower

   Case "fast"
    speed = 5 'faster

   case else 'either set the speech speed to normal OR use an absolute value (-10 to 10 - very slow to very fast)
    If IsNumeric(LCASE(WScript.Arguments.Item(1))) = True Then 'If the second parameter is a number then
     If CInt(WScript.Arguments.Item(1)) > -11 And CInt(LCASE(WScript.Arguments.Item(1))) < 11 Then 'checking that the number is between -10 and 10
      Speed = WScript.Arguments.Item(1)
     Else 'an invalid number was entered, using the standard speed.
      Speed = 0
     End If
    Else 'speed not specified, defaulting to normal
     Speed = 0
    End If
  End Select

  Speaker.Rate = speed 'set the speech speed for the speaker
  Speaker.Speak Words 'say the words as obtained earlier.

 End If
End If
