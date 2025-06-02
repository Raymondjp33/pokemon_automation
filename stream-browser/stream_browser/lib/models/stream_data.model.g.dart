// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'stream_data.model.dart';

// **************************************************************************
// JsonSerializableGenerator
// **************************************************************************

StreamData _$StreamDataFromJson(Map<String, dynamic> json) => StreamData(
      away: json['away'] as bool,
      switch1Targets: (json['switch1_targets'] as List<dynamic>?)
              ?.map((e) => TargetModel.fromJson(e as Map<String, dynamic>?))
              .toList() ??
          const [],
      switch2Targets: (json['switch2_targets'] as List<dynamic>?)
              ?.map((e) => TargetModel.fromJson(e as Map<String, dynamic>?))
              .toList() ??
          const [],
    );

Map<String, dynamic> _$StreamDataToJson(StreamData instance) =>
    <String, dynamic>{
      'away': instance.away,
      'switch1_targets':
          instance.switch1Targets.map((e) => e.toJson()).toList(),
      'switch2_targets':
          instance.switch2Targets.map((e) => e.toJson()).toList(),
    };
