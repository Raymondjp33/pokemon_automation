import '../../widgets/state_view_widget.dart';
import 'three_switch_view.dart';

class ThreeSwitch extends StateView<ThreeSwitchState> {
  ThreeSwitch({super.key})
      : super(
          stateBuilder: (context) => ThreeSwitchState(context),
          view: ThreeSwitchView(),
        );
}

class ThreeSwitchState extends StateProvider<ThreeSwitch> {
  ThreeSwitchState(super.context);
}
