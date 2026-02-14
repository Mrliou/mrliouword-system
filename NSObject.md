## NSObject  
大多數 Objective-C 類別階層的根類別，子類別繼承了執行時系統的基本介面，並具備作為 Objective-C 物件的行為能力。  
iOS 2.0+  
iPadOS 2.0+  
Mac Catalyst 13.1+  
macOS 10.0+  
tvOS 9.0+  
visionOS 1.0+  
watchOS 1.0+  
```
class NSObject

```
**[主題](https://developer.apple.com/documentation/ObjectiveC/NSObject-swift.class#topics)**  
**[初始化類別](https://developer.apple.com/documentation/ObjectiveC/NSObject-swift.class#Initializing-a-Class)**  
**[初始化類別](https://developer.apple.com/documentation/ObjectiveC/NSObject-swift.class#Initializing-a-Class)**  
```
class func initialize()

```
在類別收到第一個訊息前就初始化該類別。  
```
class func load()

```
每當 Objective-C 執行時新增類別或類別時會呼叫;實作此方法，在載入時執行類別專屬行為。  
**[建立、複製與釋放物件](https://developer.apple.com/documentation/ObjectiveC/NSObject-swift.class#Creating-Copying-and-Deallocating-Objects)**  
**[建立、複製與釋放物件](https://developer.apple.com/documentation/ObjectiveC/NSObject-swift.class#Creating-Copying-and-Deallocating-Objects)**  
```
init()

```
由子類別實作，在分配記憶體後立即初始化一個新的物件（接收器）。  
```
func copy() -> Any

```
回傳由 返回的物件。copy(with:)  
```
func mutableCopy() -> Any

```
回傳由區域所在位置返回的物件。mutableCopy(with:)nil  
**[分類](https://developer.apple.com/documentation/ObjectiveC/NSObject-swift.class#Identifying-Classes)**  
```
class func superclass() -> AnyClass?

```
回傳接收者超類別的類別物件。  
```
class func isSubclass(of: AnyClass) -> Bool

```
回傳一個布林值，指示接收類別是否為某類別的子類別，或與該類別相同。  
**[測試類別功能](https://developer.apple.com/documentation/ObjectiveC/NSObject-swift.class#Testing-Class-Functionality)**  
**[測試類別功能](https://developer.apple.com/documentation/ObjectiveC/NSObject-swift.class#Testing-Class-Functionality)**  
```
class func instancesRespond(to: Selector!) -> Bool

```
回傳一個布林值，表示接收器的實例是否能回應特定選擇器。  
**[測試協議符合性](https://developer.apple.com/documentation/ObjectiveC/NSObject-swift.class#Testing-Protocol-Conformance)**  
**[測試協議符合性](https://developer.apple.com/documentation/ObjectiveC/NSObject-swift.class#Testing-Protocol-Conformance)**  
```
class func conforms(to: Protocol) -> Bool

```
回傳一個布林值，指示目標是否符合特定協定。  
**[獲取有關方法的資訊](https://developer.apple.com/documentation/ObjectiveC/NSObject-swift.class#Obtaining-Information-About-Methods)**  
```
func method(for: Selector!) -> IMP!

```
定位並回傳接收方實作方法的位址，以便將其作為函式呼叫。  
```
class func instanceMethod(for: Selector!) -> IMP!

```
由特定選擇器定位並回傳實例方法實作的位址。  
**[描述物件](https://developer.apple.com/documentation/ObjectiveC/NSObject-swift.class#Describing-Objects)**  
**[描述物件](https://developer.apple.com/documentation/ObjectiveC/NSObject-swift.class#Describing-Objects)**  
```
class func description() -> String

```
回傳一個字串，代表接收類別的內容。  
**[支援可丟棄內容](https://developer.apple.com/documentation/ObjectiveC/NSObject-swift.class#Supporting-Discardable-Content)**  
```
var autoContentAccessingProxy: Any

```
接收物件的代理  
**[傳送訊息](https://developer.apple.com/documentation/ObjectiveC/NSObject-swift.class#Sending-Messages)**  
**[傳送訊息](https://developer.apple.com/documentation/ObjectiveC/NSObject-swift.class#Sending-Messages)**  
```
func perform(Selector, with: Any?, afterDelay: TimeInterval)

```
在延遲後，以預設模式呼叫接收端在當前執行緒上的方法。  
```
func perform(Selector, with: Any?, afterDelay: TimeInterval, inModes: [RunLoop.Mode])

```
在延遲後，呼叫接收端在當前執行緒上使用指定模式的方法。  
```
func performSelector(onMainThread: Selector, with: Any?, waitUntilDone: Bool)

```
在主執行緒中以預設模式呼叫接收端的方法。  
```
func performSelector(onMainThread: Selector, with: Any?, waitUntilDone: Bool, modes: [String]?)

```
在主執行緒上呼叫接收端的方法，使用指定模式。  
```
func perform(Selector, on: Thread, with: Any?, waitUntilDone: Bool)

```
在指定執行緒上，使用預設模式呼叫接收端的方法。  
```
func perform(Selector, on: Thread, with: Any?, waitUntilDone: Bool, modes: [String]?)

```
在指定執行緒上呼叫接收端的方法，使用指定模式。  
```
func performSelector(inBackground: Selector, with: Any?)

```
在新的背景執行緒中呼叫接收者的方法。  
```
class func cancelPreviousPerformRequests(withTarget: Any)

```
取消會執行先前以 ++[perform（_：with：afterDelay：）](https://developer.apple.com/documentation/objectivec/nsobject-swift.class/perform(_:with:afterdelay:))++ 實例方法登錄的請求。  
```
class func cancelPreviousPerformRequests(withTarget: Any, selector: Selector, object: Any?)

```
取消執行先前在 ++[perform（_：with：afterDelay：）](https://developer.apple.com/documentation/objectivec/nsobject-swift.class/perform(_:with:afterdelay:))++登錄的請求。  
**[轉發訊息](https://developer.apple.com/documentation/ObjectiveC/NSObject-swift.class#Forwarding-Messages)**  
```
func forwardingTarget(for: Selector!) -> Any?

```
回傳應先導向未識別訊息的物件。  
**[動態解析方法](https://developer.apple.com/documentation/ObjectiveC/NSObject-swift.class#Dynamically-Resolving-Methods)**  
**[動態解析方法](https://developer.apple.com/documentation/ObjectiveC/NSObject-swift.class#Dynamically-Resolving-Methods)**  
```
class func resolveClassMethod(Selector!) -> Bool

```
動態地為特定類別方法的選擇器提供實作。  
```
class func resolveInstanceMethod(Selector!) -> Bool

```
動態地為某個實例方法提供特定選擇器的實作。  
**[處理錯誤](https://developer.apple.com/documentation/ObjectiveC/NSObject-swift.class#Handling-Errors)**  
**[處理錯誤](https://developer.apple.com/documentation/ObjectiveC/NSObject-swift.class#Handling-Errors)**  
```
func doesNotRecognizeSelector(Selector!)

```
處理接收者不認識的訊息。  
**[檔案整理](https://developer.apple.com/documentation/ObjectiveC/NSObject-swift.class#Archiving)**  
**[檔案整理](https://developer.apple.com/documentation/ObjectiveC/NSObject-swift.class#Archiving)**  
```
func awakeAfter(using: NSCoder) -> Any?

```
被子類覆寫，以替換先前解碼並接收此訊息的物件。  
```
var classForArchiver: AnyClass?

```
在歸檔時，用來替代接收端自己的類別。  
```
var classForCoder: AnyClass

```
在編碼過程中，子類別會覆蓋以取代非自身類別。  
```
var classForKeyedArchiver: AnyClass?

```
子類別用來替換新類別，以取代鍵控歸檔期間的實例。  
```
class func classFallbacksForKeyedArchiver() -> [String]

```
覆寫以回傳可用於解碼物件的類別名稱，若類別無法使用。  
```
class func classForKeyedUnarchiver() -> AnyClass

```
在鍵化解檔時，子類別會覆寫以替換新類別。  
```
func replacementObject(for: NSArchiver) -> Any?

```
在歸檔時，子類別會覆寫以替換另一個物件。  
已棄用  
已棄用  
```
func replacementObject(for: NSCoder) -> Any?

```
在編碼過程中，會被子類覆蓋以替換另一個物件。  
```
func replacementObject(for: NSKeyedArchiver) -> Any?

```
在鍵控歸檔期間，子類會覆寫以替換另一個物件。  
```
class func setVersion(Int)

```
設定接收端的版本號。  
```
class func version() -> Int

```
回傳分配給類別的版本號。  
**[使用類別描述](https://developer.apple.com/documentation/ObjectiveC/NSObject-swift.class#Working-with-Class-Descriptions)**  
**[使用類別描述](https://developer.apple.com/documentation/ObjectiveC/NSObject-swift.class#Working-with-Class-Descriptions)**  
```
var attributeKeys: [String]

```
一個包含接收者類別實例所包含不變值名稱的物件陣列。NSString  
```
var classDescription: NSClassDescription

```
一個包含接收者類別屬性與關係資訊的物件。  
```
func inverse(forRelationshipKey: String) -> String?

```
對於定義接收者類別到另一類別關係名稱的鍵，會回傳該類別到接收者類別的關係名稱。  
```
var toManyRelationshipKeys: [String]

```
一個包含接收器 to-many 關係屬性鍵數的陣列。  
```
var toOneRelationshipKeys: [String]

```
接收者的一對一關係特性（若有的話）的鍵。  
**[提升無障礙性](https://developer.apple.com/documentation/ObjectiveC/NSObject-swift.class#Improving-Accessibility)**  
**[提升無障礙性](https://developer.apple.com/documentation/ObjectiveC/NSObject-swift.class#Improving-Accessibility)**  
  
[UIAccessibility](https://developer.apple.com/documentation/UIKit/uiaccessibility-protocol)  
一組提供應用程式使用者介面中檢視與控制項無障礙資訊的方法。  
  
[UIAccessibility容器](https://developer.apple.com/documentation/UIKit/uiaccessibilitycontainer)  
提供一組方法，讓子類別以獨立元素可存取子元件。  
  
[UIAccessibility行動](https://developer.apple.com/documentation/objectivec/uiaccessibilityaction)  
一組無障礙元素可用來支援特定動作的方法。  
  
[UIAccessibility焦點](https://developer.apple.com/documentation/objectivec/uiaccessibilityfocus)  
這是一種非正式的協議，提供判斷輔助應用程式（如 VoiceOver）是否專注於無障礙元素的方法。  
  
[UIAccessibility拖曳](https://developer.apple.com/documentation/objectivec/uiaccessibilitydragging)  
這兩個特性讓你能微調拖放在輔助技術下的影響。  
**[提升瀏覽器無障礙性](https://developer.apple.com/documentation/ObjectiveC/NSObject-swift.class#Improving-browser-accessibility)**  
```
func browserAccessibilityAttributedValue(in: NSRange) -> NSAttributedString

```
回傳該元素在指定範圍內的值，作為帶有屬性的字串。  
```
func browserAccessibilityDeleteTextAtCursor(numberOfCharacters: Int)

```
刪除當前游標位置元素中的文字。  
```
func browserAccessibilityInsertTextAtCursor(text: String)

```
在當前游標位置插入文字。  
```
func browserAccessibilitySelectedTextRange() -> NSRange

```
回傳元素中所選文字的範圍。  
```
func browserAccessibilitySetSelectedTextRange(NSRange)

```
更新元素所選的文字。  
```
func browserAccessibilityValue(in: NSRange) -> String

```
回傳該元素在指定範圍內的值。  
```
var browserAccessibilityContainerType: BEAccessibilityContainerType

```
那種容器會包含這個元素。  
```
var browserAccessibilityCurrentStatus: String?

```
一個字串，代表該元素在 aria-current 的值。  
```
var browserAccessibilityHasDOMFocus: Bool

```
一個布林值，用以表示該元素在瀏覽器文件物件模型中是否具有原生焦點。  
```
var browserAccessibilityIsRequired: Bool

```
一個布林值，代表該元素在 aria 必須時的值。  
```
var browserAccessibilityPressedState: BEAccessibilityPressedState

```
該元素的數值為詠嘆調壓制。  
```
var browserAccessibilityRoleDescription: String?

```
一串描述該元素在輔助科技中的角色。  
```
var browserAccessibilitySortDirection: String?

```
一個字串，該元素在 aria-sort 中值。  
**[腳本編寫](https://developer.apple.com/documentation/ObjectiveC/NSObject-swift.class#Scripting)**  
```
var classCode: FourCharCode

```
接收端的 Apple 事件類型代碼，該事件類型代碼儲存在物件中，該物件類別的程式碼。NSScriptClassDescription  
```
var className: String

```
A string containing the name of the class.  
```
func copyScriptingValue(Any, forKey: String, withProperties: [String : Any]) -> Any?

```
Creates and returns one or more scripting objects to be inserted into the specified relationship by copying the passed-in value and setting the properties in the copied object or objects.  
```
func newScriptingObject(of: AnyClass, forValueForKey: String, withContentsValue: Any?, properties: [String : Any]) -> Any?

```
Creates and returns an instance of a scriptable class, setting its contents and properties, for insertion into the relationship identified by the key.  
```
var scriptingProperties: [String: Any]?

```
An -keyed dictionary of the receiver’s scriptable properties.NSString  
```
func scriptingValue(for: NSScriptObjectSpecifier) -> Any?

```
Given an object specifier, returns the specified object or objects in the receiving container.  
**[Integrating with Combine](https://developer.apple.com/documentation/ObjectiveC/NSObject-swift.class#Integrating-with-Combine)**  
**[Integrating with Combine](https://developer.apple.com/documentation/ObjectiveC/NSObject-swift.class#Integrating-with-Combine)**  
```
struct KeyValueObservingPublisher

```
一個結合出版商，當觀察值改變時產生新元素。  
**[關鍵值觀察](https://developer.apple.com/documentation/ObjectiveC/NSObject-swift.class#Key-Value-Observing)**  
  
[NSKey值觀測](https://developer.apple.com/documentation/objectivec/nskeyvalueobserving)  
物件採用的非正式協定，用以接收其他物件指定屬性變更的通知。  
**[鍵值編碼](https://developer.apple.com/documentation/ObjectiveC/NSObject-swift.class#Key-Value-Coding)**  
  
[NSKey價值綁定建立](https://developer.apple.com/documentation/objectivec/nskeyvaluebindingcreation)  
一組你可以用來建立和移除檢視物件與控制器之間，或控制器與模型物件之間綁定的方法。  
  
[NSKey價值編碼](https://developer.apple.com/documentation/objectivec/nskeyvaluecoding)  
一種可以透過名稱或鍵間接存取物件屬性的機制。  
  
[NSScript鍵值編碼](https://developer.apple.com/documentation/objectivec/nsscriptkeyvaluecoding)  
一系列提供額外功能以處理鍵值編碼的方法。  
  
[NSScript鍵值編碼例外名稱](https://developer.apple.com/documentation/objectivec/nsscriptkeyvaluecoding-exception-names)  
由鍵值編碼方法所提出的例外。  
**[與網頁外掛互動](https://developer.apple.com/documentation/ObjectiveC/NSObject-swift.class#Interacting-with-Web-Plug-ins)**  
**[與網頁外掛互動](https://developer.apple.com/documentation/ObjectiveC/NSObject-swift.class#Interacting-with-Web-Plug-ins)**  
  
[網頁外掛容器](https://developer.apple.com/documentation/objectivec/webplugincontainer)  
WebPlugInContainer是一種非正式的協定，使外掛能向應用程式發送訊息。  
WebPlugInContainer是一種非正式的協定，使外掛能向應用程式發送訊息。  
  
[網頁外掛](https://developer.apple.com/documentation/objectivec/webplugin)  
非正式協定定義了使使用 WebKit 框架的應用程式與其可能使用的任何基於 WebKit 的外掛程式之間的互動方法。WebPlugIn  
非正式協定定義了使使用 WebKit 框架的應用程式與其可能使用的任何基於 WebKit 的外掛程式之間的互動方法。WebPlugIn  
**[實作網頁腳本](https://developer.apple.com/documentation/ObjectiveC/NSObject-swift.class#Implementing-Web-Scripting)**  
**[實作網頁腳本](https://developer.apple.com/documentation/ObjectiveC/NSObject-swift.class#Implementing-Web-Scripting)**  
  
[網頁腳本](https://developer.apple.com/documentation/objectivec/webscripting)  
WebScripting是一種非正式的協定，定義了類別可以實作的方法，將介面匯出到例如 JavaScript 等 WebScript 環境。  
**[支援 Cocoa Scripting](https://developer.apple.com/documentation/ObjectiveC/NSObject-swift.class#Supporting-Cocoa-Scripting)**  
**[支援 Cocoa Scripting](https://developer.apple.com/documentation/ObjectiveC/NSObject-swift.class#Supporting-Cocoa-Scripting)**  
  
[NSScriptingComparisonMethods](https://developer.apple.com/documentation/objectivec/nsscriptingcomparisonmethods)  
A collection of methods useful for comparing script objects.  
**[Deprecated](https://developer.apple.com/documentation/ObjectiveC/NSObject-swift.class#Deprecated)**  
避免在應用程式中使用已棄用的類別和協定。  
  
[已淘汰的符號](https://developer.apple.com/documentation/objectivec/deprecated-symbols)  
檢視已不再支援的符號，並找到可用來替代的符號。  
**[實例屬性](https://developer.apple.com/documentation/ObjectiveC/NSObject-swift.class#Instance-Properties)**  
**[實例屬性](https://developer.apple.com/documentation/ObjectiveC/NSObject-swift.class#Instance-Properties)**  
```
var accessibilityActivateBlock: AXBoolReturnBlock?
var accessibilityActivationPoint: CGPoint
var
```
```
 accessibilityActivationPointBlock: AXPointReturnBlock?

```
```
var
```
```
 accessibilityAttributedHint: NSAttributedString?

```
```
var
```
```
 accessibilityAttributedHintBlock: AXAttributedStringReturnBlock?

```
```
var
```
```
 accessibilityAttributedLabel: NSAttributedString?

```
```
var accessibilityAttributedLabelBlock: AXAttributedStringReturnBlock?
var accessibilityAttributedUserInputLabels: [NSAttributedString]!
var accessibilityAttributedUserInputLabelsBlock: AXAttributedStringArrayReturnBlock?
var accessibilityAttributedValue: NSAttributedString?
var
```
```
 accessibilityAttributedValueBlock: AXAttributedStringReturnBlock?

```
```
var
```
```
 accessibilityContainerType: UIAccessibilityContainerType

```
```
var accessibilityContainerTypeBlock: AXContainerTypeReturnBlock?
var accessibilityCustomActionsBlock: AXCustomActionsReturnBlock?
var accessibilityCustomRotors: [UIAccessibilityCustomRotor]?
var accessibilityCustomRotorsBlock: AXCustomRotorsReturnBlock?
var
```
```
 accessibilityDecrementBlock: AXVoidReturnBlock?

```
```
var
```
```
 accessibilityDirectTouchOptions: UIAccessibility.DirectTouchOptions

```
```
var
```
```
 accessibilityElements: [Any]?

```
```
var
```
```
 accessibilityElementsBlock: AXArrayReturnBlock?

```
```
var accessibilityElementsHidden: Bool
var accessibilityElementsHiddenBlock: AXBoolReturnBlock?
var
```
```
 accessibilityExpandedStatus: UIAccessibility.ExpandedStatus

```
```
var
```
```
 accessibilityExpandedStatusBlock: (() -> UIAccessibility.ExpandedStatus)?

```
```
var
```
```
 accessibilityFocusedUIElement: Any?

```
```
var accessibilityFrame: CGRect
var
```
```
 accessibilityFrameBlock: AXRectReturnBlock?

```
```
var
```
```
 accessibilityHeaderElements: [Any]?

```
```
var
```
```
 accessibilityHeaderElementsBlock: AXArrayReturnBlock?

```
```
var accessibilityHint: String?
var accessibilityHintBlock: AXStringReturnBlock?
var
```
```
 accessibilityIdentifierBlock: AXStringReturnBlock?

```
```
var accessibilityIncrementBlock: AXVoidReturnBlock?
var accessibilityLabel: String?
var
```
```
 accessibilityLabelBlock: AXStringReturnBlock?

```
```
var
```
```
 accessibilityLanguage: String?

```
```
var
```
```
 accessibilityLanguageBlock: AXStringReturnBlock?

```
```
var
```
```
 accessibilityMagicTapBlock: AXBoolReturnBlock?

```
```
var accessibilityNavigationStyle: UIAccessibilityNavigationStyle
var
```
```
 accessibilityNavigationStyleBlock: AXNavigationStyleReturnBlock?

```
```
var accessibilityNextTextNavigationElement: Any?
var accessibilityNextTextNavigationElementBlock: AXObjectReturnBlock?
var
```
```
 accessibilityNotifiesWhenDestroyed: Bool

```
一個布林值，指示自訂無障礙物件在對應的 UI 元素被銷毀時是否會發送通知。  
```
var accessibilityPath: UIBezierPath?
var accessibilityPathBlock: AXPathReturnBlock?
var
```
```
 accessibilityPerformEscapeBlock: AXBoolReturnBlock?

```
```
var accessibilityPreviousTextNavigationElement: Any?
var accessibilityPreviousTextNavigationElementBlock: AXObjectReturnBlock?
var
```
```
 accessibilityRespondsToUserInteraction: Bool

```
```
var
```
```
 accessibilityRespondsToUserInteractionBlock: AXBoolReturnBlock?

```
```
var accessibilityShouldGroupAccessibilityChildrenBlock: AXBoolReturnBlock?
var accessibilityTextInputResponder: (any UITextInput)?
var accessibilityTextInputResponderBlock: AXUITextInputReturnBlock?
var
```
```
 accessibilityTextualContext: UIAccessibilityTextualContext?

```
```
var
```
```
 accessibilityTextualContextBlock: AXTextualContextReturnBlock?

```
```
var accessibilityTraits: UIAccessibilityTraits
var
```
```
 accessibilityTraitsBlock: AXTraitsReturnBlock?

```
```
var accessibilityUserInputLabels: [String]!
var accessibilityUserInputLabelsBlock: AXStringArrayReturnBlock?
var accessibilityValue: String?
var accessibilityValueBlock: AXStringReturnBlock?
var
```
```
 accessibilityViewIsModal: Bool

```
```
var
```
```
 accessibilityViewIsModalBlock: AXBoolReturnBlock?

```
```
var automationElements: [Any]?
var
```
```
 automationElementsBlock: AXArrayReturnBlock?

```
```
var
```
```
 isAccessibilityElement: Bool

```
```
var
```
```
 isAccessibilityElementBlock: AXBoolReturnBlock?

```
```
var
```
```
 isSelectable: Bool

```
```
var
```
```
 objectSpecifier: NSScriptObjectSpecifier?

```
Returns an object specifier for the receiver.  
```
var shouldGroupAccessibilityChildren: Bool

```
**[Instance Methods](https://developer.apple.com/documentation/ObjectiveC/NSObject-swift.class#Instance-Methods)**  
```
func acceptsPreviewPanelControl(QLPreviewPanel!) -> Bool
func accessibilityElement(at: Int) -> Any?
func
```
```
 accessibilityElementCount() -> Int

```
```
func accessibilityHitTest(NSPoint) -> Any?
func
```
```
 accessibilityHitTest(CGPoint, event: UIEvent?) -> Any?

```
```
func
```
```
 accessibilityLineEndPositionFromCurrentSelection() -> Int

```
```
func
```
```
 accessibilityLineRange(forPosition: Int) -> NSRange

```
```
func accessibilityLineStartPositionFromCurrentSelection() -> Int
func
```
```
 accessibilityZoomIn(at: CGPoint) -> Bool

```
Zooms in on the content at the specified point.  
```
func accessibilityZoomOut(at: CGPoint) -> Bool

```
Zooms out from the content at the specified point.  
```
func actionProperty() -> String!

```
Sent to the delegate to request the property the action applies to.  
```
func attemptRecovery(fromError: any Error, optionIndex: Int) -> Bool

```
Implemented to attempt a recovery from an error noted in an application-modal dialog.  
```
func attemptRecovery(fromError: any Error, optionIndex: Int, delegate: Any?, didRecoverSelector: Selector?, contextInfo: UnsafeMutableRawPointer?)

```
Implemented to attempt a recovery from an error noted in a document-modal sheet.  
```
func authorizationViewCreatedAuthorization(SFAuthorizationView!)

```
Sent to the delegate to indicate the authorization object has been created or changed.  
```
func authorizationViewDidAuthorize(SFAuthorizationView!)

```
Sent to the delegate to indicate the user was authorized and the authorization view was changed to unlocked.  
```
func authorizationViewDidDeauthorize(SFAuthorizationView!)

```
Sent to the delegate to indicate the user was deauthorized and the authorization view was changed to locked.  
```
func authorizationViewDidHide(SFAuthorizationView!)

```
寄給代表，以表明觀點的能見度已改變。  
```
func authorizationViewReleasedAuthorization(SFAuthorizationView!)

```
發送給代表，表示即將進行授權取消。  
```
func authorizationViewShouldDeauthorize(SFAuthorizationView!) -> Bool

```
當使用者點擊開啟鎖的圖示時，會傳送給代理人。  
```
func awakeFromNib()

```
在接收器從介面建構器（Interface Builder）檔案或筆尖檔案載入後，準備接收器進行服務。  
```
func beginPreviewPanelControl(QLPreviewPanel!)
func burnProgressPanel(DRBurnProgressPanel!, burnDidFinish: DRBurn!) -> Bool

```
讓代表負責燃燒結束後的回饋。  
```
func burnProgressPanelDidFinish(Notification!)

```
是下單後小組發出的通知。  
```
func burnProgressPanelWillBegin(Notification!)

```
螢幕在顯示前發送通知。  
```
func candidates(Any!) -> [Any]!

```
回傳一組候選人。  
```
func certificatePanelShowHelp(SFCertificatePanel!) -> Bool

```
為模態面板實作自訂的幫助行為。  
```
func chooseIdentityPanelShowHelp(SFChooseIdentityPanel!) -> Bool

```
為模態面板實作自訂的幫助行為。  
```
func commitComposition(Any!)

```
通知控制器該組合應該被提交。  
```
func composedString(Any!) -> Any!

```
回傳目前已組合的字串。  
```
func compositionParameterView(QCCompositionParameterView!, didChangeParameterWithKey: String!)

```
在合成參數檢視中編輯輸入參數後呼叫。  
已棄用  
已棄用  
```
func compositionParameterView(QCCompositionParameterView!, shouldDisplayParameterWithKey: String!, attributes: [AnyHashable : Any]!) -> Bool

```
Allows you to define which composition parameters are visible in the user interface when the composition parameter view refreshes.  
Deprecated  
Deprecated  
```
func compositionPickerView(QCCompositionPickerView!, didSelect: QCComposition!)

```
Performs custom tasks when the selected composition in the composition picker view changes.  
Deprecated  
```
func compositionPickerViewDidStartAnimating(QCCompositionPickerView!)

```
Performs custom tasks when the composition picker view starts animating a composition.  
Deprecated  
```
func compositionPickerViewWillStopAnimating(QCCompositionPickerView!)

```
Performs custom tasks when the composition picker view stops animating a composition.  
Deprecated  
Deprecated  
```
func didCommand(by: Selector!, client: Any!) -> Bool

```
Processes a command generated by user action such as typing certain keys or pressing the mouse button.  
```
func doesContain(Any) -> Bool

```
Returns a Boolean value that indicates whether the receiver contains a given object.  
```
func endPreviewPanelControl(QLPreviewPanel!)
func
```
```
 eraseProgressPanel(DREraseProgressPanel!, eraseDidFinish: DRErase!) -> Bool

```
Notification sent by the panel before display.  
```
func eraseProgressPanelDidFinish(Notification!)

```
Notification sent by the panel after ordering out.  
```
func eraseProgressPanelWillBegin(Notification!)

```
Notification sent by the panel before display.  
```
func exceptionHandler(NSExceptionHandler!, shouldHandle: NSException!, mask: Int) -> Bool

```
Implemented by the delegate to evaluate whether the delegating exception handler should handle a given exception.  
```
func exceptionHandler(NSExceptionHandler!, shouldLogException: NSException!, mask: Int) -> Bool

```
Implemented by the delegate to evaluate whether the delegating exception hangler should log a given exception.  
```
func fileTransferServicesAbortComplete(OBEXFileTransferServices!, error: OBEXError)
func fileTransferServicesConnectionComplete(OBEXFileTransferServices!, error: OBEXError)
func
```
```
 fileTransferServicesCopyRemoteFileComplete(OBEXFileTransferServices!, error: OBEXError)

```
```
func
```
```
 fileTransferServicesCopyRemoteFileProgress(OBEXFileTransferServices!, transferProgress: [AnyHashable : Any]!)

```
```
func
```
```
 fileTransferServicesCreateFolderComplete(OBEXFileTransferServices!, error: OBEXError, folder: String!)

```
```
func
```
```
 fileTransferServicesDisconnectionComplete(OBEXFileTransferServices!, error: OBEXError)

```
```
func fileTransferServicesFilePreparationComplete(OBEXFileTransferServices!, error: OBEXError)
func fileTransferServicesPathChangeComplete(OBEXFileTransferServices!, error: OBEXError, finalPath: String!)
func
```
```
 fileTransferServicesRemoveItemComplete(OBEXFileTransferServices!, error: OBEXError, removedItem: String!)

```
```
func
```
```
 fileTransferServicesRetrieveFolderListingComplete(OBEXFileTransferServices!, error: OBEXError, listing: [Any]!)

```
```
func fileTransferServicesSendFileComplete(OBEXFileTransferServices!, error: OBEXError)
func
```
```
 fileTransferServicesSendFileProgress(OBEXFileTransferServices!, transferProgress: [AnyHashable : Any]!)

```
```
func
```
```
 handle(NSEvent!, client: Any!) -> Bool

```
Handles key down and mouse events.  
```
func imageBrowser(IKImageBrowserView!, backgroundWasRightClickedWith: NSEvent!)

```
Performs custom tasks when the user right-clicks the image browser view background.  
```
func imageBrowser(IKImageBrowserView!, cellWasDoubleClickedAt: Int)

```
Performs custom tasks when the user double-clicks an item in the image browser view.  
```
func imageBrowser(IKImageBrowserView!, cellWasRightClickedAt: Int, with: NSEvent!)

```
Performs custom tasks when the user right-clicks an item in the image browser view.  
```
func imageBrowser(IKImageBrowserView!, groupAt: Int) -> [AnyHashable : Any]!

```
Returns the group at the specified index.  
```
func imageBrowser(IKImageBrowserView!, itemAt: Int) -> Any!

```
Returns an object for the item in an image browser view that corresponds to the specified index.  
```
func imageBrowser(IKImageBrowserView!, moveItemsAt: IndexSet!, to: Int) -> Bool

```
Signals that the specified items should be moved to the specified destination.  
```
func imageBrowser(IKImageBrowserView!, removeItemsAt: IndexSet!)

```
Signals that a remove operation should be applied to the specified items.  
```
func imageBrowser(IKImageBrowserView!, writeItemsAt: IndexSet!, to: NSPasteboard!) -> Int

```
Signals that a drag should begin.  
```
func imageBrowserSelectionDidChange(IKImageBrowserView!)

```
Performs custom tasks when the selection changes.  
```
func imageRepresentation() -> Any!

```
Returns the image to display.  
```
func imageRepresentationType() -> String!

```
Returns the representation type of the image to display.  
```
func imageSubtitle() -> String!

```
Returns the display subtitle of the image.  
```
func imageTitle() -> String!

```
Returns the display title of the image.  
```
func imageUID() -> String!

```
Returns a unique string that identifies the data source item.  
```
func imageVersion() -> Int

```
Returns the version of the item.  
```
func index(ofAccessibilityElement: Any) -> Int
func indicesOfObjects(byEvaluatingObjectSpecifier: NSScriptObjectSpecifier) -> [NSNumber]?

```
回傳指定容器物件的索引。  
```
func inputText(String!, client: Any!) -> Bool

```
處理不映射到動作方法的鍵下事件。  
```
func inputText(String!, key: Int, modifiers: Int, client: Any!) -> Bool

```
接收 Unicode、產生 Unicode 的關鍵程式碼，以及任何修飾符標誌。  
```
func isCaseInsensitiveLike(String) -> Bool

```
回傳一個布林值，表示當忽略接收器中字元的情況時，接收器是否被視為「類似」某個字串。  
```
func isEqual(to: Any?) -> Bool

```
回傳一個布林值，表示接收者是否等於另一個給定物件。  
```
func isGreaterThan(Any?) -> Bool

```
回傳一個布林值，表示接收者是否高於另一個給定物件。  
```
func isGreaterThanOrEqual(to: Any?) -> Bool

```
回傳一個布林值，表示接收者是大於或等於另一個給定物件。  
```
func isLessThan(Any?) -> Bool

```
回傳一個布林值，表示接收器是否低於其他給定物件。  
```
func isLessThanOrEqual(to: Any?) -> Bool

```
回傳一個布林值，表示接收者是小於或等於另一個給定物件。  
```
func isLike(String) -> Bool

```
回傳一個布林值，表示接收者是否「像」另一個特定物件。  
```
func isNotEqual(to: Any?) -> Bool

```
回傳一個布林值，表示接收者是否等於另一個給定物件。  
```
func numberOfGroups(inImageBrowser: IKImageBrowserView!) -> Int

```
在影像瀏覽器檢視中回傳群組數量。  
```
func numberOfItems(inImageBrowser: IKImageBrowserView!) -> Int

```
回傳資料來源物件所管理的記錄數量。  
```
func originalString(Any!) -> NSAttributedString!

```
回傳由預組合 Unicode 字元組成的字串。  
```
func performAction(for: ABPerson!, identifier: String!)

```
被派往代表執行該行動。  
```
func prepareForInterfaceBuilder()

```
當在介面建構器中建立可設計物件時呼叫。  
```
func provideImage(to: any MTLTexture, commandBuffer: any MTLCommandBuffer, originx: Int, originy: Int, width: Int, height: Int, userInfo: Any?)

```
這是影像提供者物件方式實作的一種可選方法。  
透過此方法，提供者物件可利用 Metal API 在影像物件渲染時，將像素  
資料提供至 MTLTexture。  
```
func provideImageData(UnsafeMutableRawPointer, bytesPerRow: Int, origin: Int, Int, size: Int, Int, userInfo: Any?)

```
提供資料給物件。CIImage  
```
func quartzFilterManager(QuartzFilterManager!, didAdd: QuartzFilter!)
func quartzFilterManager(QuartzFilterManager!, didModifyFilter: QuartzFilter!)
func
```
```
 quartzFilterManager(QuartzFilterManager!, didRemove: QuartzFilter!)

```
```
func
```
```
 quartzFilterManager(QuartzFilterManager!, didSelect: QuartzFilter!)

```
```
func readLinkQuality(forDeviceComplete: Any!, device: IOBluetoothDevice!, info: UnsafeMutablePointer<BluetoothHCILinkQualityInfo>!, error: IOReturn)
func
```
```
 readRSSI(forDeviceComplete: Any!, device: IOBluetoothDevice!, info: UnsafeMutablePointer<BluetoothHCIRSSIInfo>!, error: IOReturn)

```
```
func
```
```
 saveOptions(IKSaveOptions!, shouldShowUTType: String!) -> Bool

```
呼叫以判斷是否應該在儲存面板顯示指定的統一類型識別碼。  
```
func setSharedObservers(NSKeyValueSharedObserversSnapshot?)
func
```
```
 setupPanel(DRSetupPanel!, determineBestDeviceOfA: DRDevice!, orB: DRDevice!) -> DRDevice!

```
允許委託人指定其偏好的裝置。  
```
func setupPanel(DRSetupPanel!, deviceContainsSuitableMedia: DRDevice!, promptString: AutoreleasingUnsafeMutablePointer<NSString?>!) -> Bool

```
此代理方法允許代理判斷插入裝置中的媒體是否適合執行任何操作。  
```
func setupPanel(DRSetupPanel!, deviceCouldBeTarget: DRDevice!) -> Bool

```
允許代表判斷該裝置是否可作為目標使用。  
```
func setupPanelDeviceSelectionChanged(Notification!)

```
當面板中的裝置選擇改變時，預設通知中心會發送。  
```
func setupPanelShouldHandleMediaReservations(DRSetupPanel!) -> Bool

```
此代表制讓代表能控制媒體預約的處理方式。  
```
func shouldEnableAction(for: ABPerson!, identifier: String!) -> Bool

```
送交代表判斷是否應啟用該動作。  
```
func title(for: ABPerson!, identifier: String!) -> String!

```
送給代表，請求行動菜單項目的標題。  
```
func workflowController(AMWorkflowController, didError: any Error)

```
已棄用  
```
func workflowController(AMWorkflowController, didRun: AMAction)

```
已棄用  
```
func workflowController(AMWorkflowController, willRun: AMAction)

```
已棄用  
```
func workflowControllerDidRun(AMWorkflowController)

```
已棄用  
```
func workflowControllerDidStop(AMWorkflowController)

```
已棄用  
```
func workflowControllerWillRun(AMWorkflowController)

```
已棄用  
```
func workflowControllerWillStop(AMWorkflowController)

```
已棄用  
**[型別方法](https://developer.apple.com/documentation/ObjectiveC/NSObject-swift.class#Type-Methods)**  
**[型別方法](https://developer.apple.com/documentation/ObjectiveC/NSObject-swift.class#Type-Methods)**  
```
class func debugDescription() -> String
class
```
```
 func hash() -> Int

```
**[預設實作](https://developer.apple.com/documentation/ObjectiveC/NSObject-swift.class#Default-Implementations)**  
  
[等值實作](https://developer.apple.com/documentation/objectivec/nsobject-swift.class/equatable-implementations)  
  
[可哈希實作](https://developer.apple.com/documentation/objectivec/nsobject-swift.class/hashable-implementations)  
**[人際關係](https://developer.apple.com/documentation/ObjectiveC/NSObject-swift.class#relationships)**  
**[人際關係](https://developer.apple.com/documentation/ObjectiveC/NSObject-swift.class#relationships)**  
**[符合](https://developer.apple.com/documentation/ObjectiveC/NSObject-swift.class#conforms-to)**  
* [CVarArg](https://developer.apple.com/documentation/Swift/CVarArg)  
* [Copyable](https://developer.apple.com/documentation/Swift/Copyable)  
* [CustomDebugStringConvertible](https://developer.apple.com/documentation/Swift/CustomDebugStringConvertible)  
* [CustomStringConvertible](https://developer.apple.com/documentation/Swift/CustomStringConvertible)  
* [Equatable](https://developer.apple.com/documentation/Swift/Equatable)  
* [Hashable](https://developer.apple.com/documentation/Swift/Hashable)  
* [NSObjectProtocol](https://developer.apple.com/documentation/objectivec/nsobjectprotocol)  
