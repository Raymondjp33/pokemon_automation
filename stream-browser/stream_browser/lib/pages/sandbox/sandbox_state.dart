import '../../widgets/state_view_widget.dart';
import 'sandbox_view.dart';

class Sandbox extends StateView<SandboxState> {
  Sandbox({super.key})
      : super(
          stateBuilder: (context) => SandboxState(context),
          view: SandboxView(),
        );
}

class SandboxState extends StateProvider<Sandbox> {
  SandboxState(super.context);
}
