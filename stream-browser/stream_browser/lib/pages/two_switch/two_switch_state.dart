import '../../widgets/state_view_widget.dart';
import 'two_switch_view.dart';

class TwoSwitch extends StateView<TwoSwitchState> {
  TwoSwitch({super.key})
      : super(
          stateBuilder: (context) => TwoSwitchState(context),
          view: TwoSwitchView(),
        );
}

class TwoSwitchState extends StateProvider<TwoSwitch> {
  TwoSwitchState(super.context);
}
